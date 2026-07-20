"""
NOTE: as of the read-only redesign, this module is no longer imported
by main.py — the API has no endpoints that can trigger the pipeline.
Kept here in case you want to revisit automated/scheduled runs later
(e.g. a cron-triggered T-15 refresh with no human in the loop at all).

Runs the Kudurebaala pipeline scripts as subprocesses and streams their
output. Each run gets a job_id; multiple SSE clients can attach to the
same job_id and each gets the full backlog + live tail.

Confirmed CLI shapes:
    run_experts.py  --graph <uri> --folder <path> [--only NAME [NAME...]] [--force]
    run_analysis.py --graph <uri> --folder <path> [--query "..."]
                     (prints synthesis to stdout — does NOT write a cache
                      file, so we capture stdout and write one ourselves)
    run_pipeline.py --graph <uri> --folder <path>
                     (CLI shape unconfirmed — assumed to match the other
                      two scripts' --graph/--folder convention; adjust
                      _run_full_pipeline() below if it differs)

Two entry points:
  - start_full_pipeline(race_id)   -> run_pipeline -> run_experts -> run_analysis
  - start_phase2_rerun(race_id)    -> run_experts.py --only field_rivals --force
                                       (field_rivals decides Phase 1 vs
                                       Phase 2 internally based on
                                       whether live odds are in the graph
                                       yet — we just have to force it to
                                       run again)
"""
import asyncio
import uuid
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import config


@dataclass
class Job:
    job_id: str
    race_id: str
    kind: str  # "full_pipeline" | "phase2_rerun"
    status: str = "running"  # running | done | error
    lines: list[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    error: Optional[str] = None
    _subscribers: list[asyncio.Queue] = field(default_factory=list)

    def emit(self, line: str):
        self.lines.append(line)
        for q in self._subscribers:
            q.put_nowait(line)

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        for line in self.lines:  # replay backlog
            q.put_nowait(line)
        if self.status != "running":
            q.put_nowait(f"__END__:{self.status}")
        else:
            self._subscribers.append(q)
        return q

    def finish(self, status: str, error: Optional[str] = None):
        self.status = status
        self.error = error
        self.finished_at = time.time()
        for q in self._subscribers:
            q.put_nowait(f"__END__:{status}")
        self._subscribers.clear()


JOBS: dict[str, Job] = {}


def graph_uri_for(race_id: str) -> str:
    return f"{config.GRAPH_URI_PREFIX}{race_id}"


def race_dir_for(race_id: str) -> Path:
    return config.RACE_DATA_ROOT / race_id


def find_race_card_csv(race_id: str) -> Path:
    """
    run_pipeline.py takes --csv, not --graph/--folder like the other two
    scripts. The race card lives at {race_folder}/race_card/*.csv
    (e.g. race_card/Race_Card_BANGALORE_12_JuL_2026_race_4.csv).
    """
    race_card_dir = race_dir_for(race_id) / "race_card"
    if not race_card_dir.exists():
        raise FileNotFoundError(f"No race_card/ folder for {race_id} at {race_card_dir}")
    csvs = sorted(race_card_dir.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No race card CSV found in {race_card_dir}")
    if len(csvs) > 1:
        raise RuntimeError(
            f"Multiple race card CSVs found in {race_card_dir}: {[c.name for c in csvs]} — expected exactly one"
        )
    return csvs[0]


async def _stream_subprocess(job: Job, cmd: list[str], cwd: str, capture: Optional[list[str]] = None):
    job.emit(f"$ {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    assert proc.stdout is not None
    while True:
        raw = await proc.stdout.readline()
        if not raw:
            break
        line = raw.decode(errors="replace").rstrip()
        job.emit(line)
        if capture is not None:
            capture.append(line)
    code = await proc.wait()
    if code != 0:
        raise RuntimeError(f"{cmd[0]} exited with code {code}")


def _save_synthesis_from_output(race_id: str, output_lines: list[str]):
    """
    run_analysis.py prints a divider line containing
    'CHIEF HANDICAPPER SYNTHESIS' then the synthesis text. Grab
    everything after that divider block and write it to our own
    cache file so it survives without re-running the LLM.
    """
    text = "\n".join(output_lines)
    marker = "CHIEF HANDICAPPER SYNTHESIS"
    idx = text.find(marker)
    if idx == -1:
        synthesis = text  # fallback: save everything rather than lose it
    else:
        # skip past the marker line and the '====' divider line after it
        rest = text[idx:]
        parts = rest.split("\n", 2)
        synthesis = parts[2] if len(parts) > 2 else rest

    out_file = race_dir_for(race_id) / config.EXPERT_CACHE_DIRNAME / config.FINAL_ANALYSIS_FILENAME
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(synthesis.strip() + "\n", encoding="utf-8")


async def _run_full_pipeline(job: Job):
    folder = str(race_dir_for(job.race_id))
    graph = graph_uri_for(job.race_id)
    scripts = str(config.PIPELINE_SCRIPTS_ROOT)
    py = config.PIPELINE_PYTHON
    try:
        job.emit("=== run_pipeline.py (ingestion) ===")
        try:
            csv_path = find_race_card_csv(job.race_id)
        except (FileNotFoundError, RuntimeError) as e:
            job.emit(f"[ERROR] {e}")
            job.finish("error", error=str(e))
            return
        job.emit(f"  race card: {csv_path}")
        await _stream_subprocess(
            job,
            [py, str(config.PIPELINE_SCRIPTS_ROOT / "run_pipeline.py"), "--csv", str(csv_path)],
            cwd=scripts,
        )

        job.emit("=== run_experts.py (all 10 experts) ===")
        await _stream_subprocess(
            job,
            [py, str(config.PIPELINE_SCRIPTS_ROOT / "run_experts.py"), "--graph", graph, "--folder", folder],
            cwd=scripts,
        )

        job.emit("=== run_analysis.py (synthesizer) ===")
        captured: list[str] = []
        await _stream_subprocess(
            job,
            [py, str(config.PIPELINE_SCRIPTS_ROOT / "run_analysis.py"), "--graph", graph, "--folder", folder],
            cwd=scripts,
            capture=captured,
        )
        _save_synthesis_from_output(job.race_id, captured)

        job.finish("done")
    except Exception as e:
        job.emit(f"[ERROR] {e}")
        job.finish("error", error=str(e))


async def _run_phase2_rerun(job: Job):
    """
    T-15 minute window: re-invoke expert_field_rivals with --force.
    The expert itself decides Phase 1 vs Phase 2 based on whether live
    odds are present in the graph yet — we're just triggering the rerun,
    not choosing the phase. Also re-runs the synthesizer afterward so
    the final selection reflects the fresh field_rivals read.
    """
    folder = str(race_dir_for(job.race_id))
    graph = graph_uri_for(job.race_id)
    scripts = str(config.PIPELINE_SCRIPTS_ROOT)
    py = config.PIPELINE_PYTHON
    try:
        job.emit("=== run_experts.py --only field_rivals --force ===")
        await _stream_subprocess(
            job,
            [py, str(config.PIPELINE_SCRIPTS_ROOT / "run_experts.py"),
             "--graph", graph, "--folder", folder,
             "--only", "field_rivals", "--force"],
            cwd=scripts,
        )

        job.emit("=== run_analysis.py (re-synthesize with fresh field_rivals) ===")
        captured: list[str] = []
        await _stream_subprocess(
            job,
            [py, str(config.PIPELINE_SCRIPTS_ROOT / "run_analysis.py"), "--graph", graph, "--folder", folder],
            cwd=scripts,
            capture=captured,
        )
        _save_synthesis_from_output(job.race_id, captured)

        job.finish("done")
    except Exception as e:
        job.emit(f"[ERROR] {e}")
        job.finish("error", error=str(e))


def start_full_pipeline(race_id: str) -> Job:
    job = Job(job_id=str(uuid.uuid4()), race_id=race_id, kind="full_pipeline")
    JOBS[job.job_id] = job
    asyncio.create_task(_run_full_pipeline(job))
    return job


def start_phase2_rerun(race_id: str) -> Job:
    job = Job(job_id=str(uuid.uuid4()), race_id=race_id, kind="phase2_rerun")
    JOBS[job.job_id] = job
    asyncio.create_task(_run_phase2_rerun(job))
    return job


def get_job(job_id: str) -> Optional[Job]:
    return JOBS.get(job_id)
