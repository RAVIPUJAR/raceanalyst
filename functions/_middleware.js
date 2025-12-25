async function checkCloudflareAuth() {
        try {
            console.log("🔐 Checking Cloudflare authentication...");
            
            // Add timestamp to prevent caching
            const timestamp = new Date().getTime();
            
            // Try BOTH endpoints - first the proxy, then direct Worker as fallback
            let response;
            let usedProxy = true;
            
            try {
                console.log("Trying proxy endpoint: /api/auth-status");
                response = await fetch(`/api/auth-status?t=${timestamp}`, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                });
                console.log("Proxy response status:", response.status);
            } catch (proxyError) {
                console.warn("Proxy failed, trying direct Worker:", proxyError.message);
                usedProxy = false;
                
                // Fallback to direct Worker URL
                response = await fetch(`https://broad-sound-fdb7.raceanalyst.workers.dev/auth-status?t=${timestamp}`, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache'
                    }
                });
                console.log("Direct Worker response status:", response.status);
            }
            
            console.log(`Auth check via ${usedProxy ? 'proxy' : 'direct Worker'}: ${response.status}`);
            
            if (response.ok) {
                const text = await response.text();
                console.log("Raw response:", text.substring(0, 200));
                
                let data;
                try {
                    data = JSON.parse(text);
                } catch (e) {
                    console.error("Failed to parse JSON:", e);
                    data = {};
                }
                
                console.log("Auth data received:", data);
                
                // Check if authenticated - be more flexible with the check
                const isAuth = data.authenticated === true || 
                              data.authenticated === "true" ||
                              data.email || 
                              data.user ||
                              (response.headers.get('cf-access-authenticated-user-email'));
                
                if (isAuth) {
                    currentUser = {
                        email: data.email || data.user?.email || 'admin@raceanalyst.in',
                        name: data.name || data.user?.name || data.email || 'Admin',
                        authenticated: true
                    };
                    isAuthenticated = true;
                    
                    console.log(`✅ Authenticated as: ${currentUser.name} (${currentUser.email})`);
                    return { 
                        authenticated: true, 
                        user: currentUser,
                        data: data,
                        viaProxy: usedProxy
                    };
                }
            } else if (response.status === 401) {
                console.log("❌ Not authenticated (401)");
            }
            
            // Not authenticated
            currentUser = null;
            isAuthenticated = false;
            console.log("❌ Not authenticated");
            return { 
                authenticated: false, 
                user: null,
                status: response.status,
                viaProxy: usedProxy
            };
            
        } catch (error) {
            console.error("Auth check failed:", error);
            currentUser = null;
            isAuthenticated = false;
            return { 
                authenticated: false, 
                user: null, 
                error: error.message 
            };
        }
    }
