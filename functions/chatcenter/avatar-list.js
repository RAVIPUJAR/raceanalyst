// functions/chatcenter/avatar-list.js
export async function onRequest(context) {
  // Define all possible avatars you have
  const allAvatars = [
    'svg-1.svg', 'svg-2.svg', 'svg-3.svg', 'svg-4.svg',
    'svg-5.svg', 'svg-6.svg', 'svg-7.svg', 'svg-8.svg',
    'svg-9.svg', 'svg-10.svg', 'svg-11.svg', 'svg-12.svg'
    // Add all your actual avatar filenames here
  ];
  
  // Filter to only return avatars that exist
  const existingAvatars = await filterExistingAvatars(context, allAvatars);
  
  return new Response(JSON.stringify(existingAvatars), {
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=3600' // 1 hour
    }
  });
}

async function filterExistingAvatars(context, avatarList) {
  const existing = [];
  
  for (const avatar of avatarList) {
    try {
      const url = new URL(`/chatcenter/avatar/${avatar}`, context.request.url);
      const response = await context.env.ASSETS.fetch(new Request(url));
      
      if (response.status === 200) {
        existing.push(avatar);
      }
    } catch (err) {
      // Avatar doesn't exist
    }
  }
  
  return existing.length > 0 ? existing : ['svg-1.svg', 'svg-2.svg'];
}
