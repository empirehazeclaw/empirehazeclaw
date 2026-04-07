// DSGVO Cookie Banner (No-Code Integration)
document.addEventListener("DOMContentLoaded", function() {
    if(!localStorage.getItem("cookie_consent")) {
        let banner = document.createElement("div");
        banner.innerHTML = `
            <div style="position:fixed; bottom:0; width:100%; background:#1a1a1a; color:white; padding:20px; text-align:center; z-index:9999; border-top: 1px solid #333; font-family: sans-serif;">
                <p style="margin: 0 0 15px 0; font-size: 14px;">Wir verwenden Cookies und Local Storage, um unsere Website (wie z.B. den Warenkorb) für Sie zu optimieren. Es werden keine Tracking-Daten an Dritte (wie Facebook/Google) gesendet.</p>
                <button id="acceptCookies" style="background:#00ff88; color:#000; border:none; padding:10px 25px; cursor:pointer; font-weight:bold; border-radius: 4px;">Zustimmen</button>
                <a href="/datenschutz" style="color:#aaa; text-decoration:underline; font-size:12px; margin-left: 15px;">Datenschutz</a>
            </div>
        `;
        document.body.appendChild(banner);
        
        document.getElementById("acceptCookies").addEventListener("click", function() {
            localStorage.setItem("cookie_consent", "true");
            banner.style.display = "none";
        });
    }
});
