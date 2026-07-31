import os
import random

def generate_svg_doodles():
    out_dir = 'floating_doodles'
    os.makedirs(out_dir, exist_ok=True)
    
    # Palette
    colors = ['#2563EB', '#60A5FA', '#93C5FD', '#FFFFFF']
    
    # 1. Scales of Justice
    scales = f"""<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <path d="M 40 10 L 40 70 M 20 30 L 60 30 M 20 30 L 10 50 L 30 50 Z M 60 30 L 50 50 L 70 50 Z M 25 70 L 55 70" fill="none" stroke="#2563EB" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.12"/>
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2563EB" stop-opacity="0.15" />
            <stop offset="100%" stop-color="#60A5FA" stop-opacity="0" />
        </linearGradient>
    </defs>
    <path d="M 10 50 C 15 60 25 60 30 50 Z" fill="url(#grad1)"/>
    <path d="M 50 50 C 55 60 65 60 70 50 Z" fill="url(#grad1)"/>
</svg>"""
    
    # 2. Gavel (Judge's hammer)
    gavel = f"""<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <g transform="rotate(30 40 40)">
        <rect x="25" y="20" width="30" height="15" rx="3" fill="none" stroke="#60A5FA" stroke-width="4" opacity="0.15"/>
        <line x1="40" y1="35" x2="40" y2="65" stroke="#60A5FA" stroke-width="6" stroke-linecap="round" opacity="0.15"/>
        <line x1="20" y1="27.5" x2="25" y2="27.5" stroke="#60A5FA" stroke-width="4" stroke-linecap="round" opacity="0.15"/>
        <line x1="55" y1="27.5" x2="60" y2="27.5" stroke="#60A5FA" stroke-width="4" stroke-linecap="round" opacity="0.15"/>
        <rect x="20" y="70" width="40" height="5" rx="2" fill="#60A5FA" opacity="0.1"/>
    </g>
</svg>"""

    # 3. Courthouse Pillar (Government building)
    pillar = f"""<svg width="70" height="90" viewBox="0 0 70 90" xmlns="http://www.w3.org/2000/svg">
    <polygon points="35,10 10,30 60,30" fill="url(#grad2)" opacity="0.1"/>
    <polygon points="35,10 10,30 60,30" fill="none" stroke="#93C5FD" stroke-width="3" stroke-linejoin="round" opacity="0.15"/>
    <line x1="20" y1="30" x2="20" y2="70" stroke="#93C5FD" stroke-width="6" stroke-linecap="square" opacity="0.12"/>
    <line x1="35" y1="30" x2="35" y2="70" stroke="#93C5FD" stroke-width="6" stroke-linecap="square" opacity="0.12"/>
    <line x1="50" y1="30" x2="50" y2="70" stroke="#93C5FD" stroke-width="6" stroke-linecap="square" opacity="0.12"/>
    <rect x="5" y="70" width="60" height="10" fill="none" stroke="#93C5FD" stroke-width="3" opacity="0.15"/>
    <defs>
        <linearGradient id="grad2" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#93C5FD" stop-opacity="1" />
            <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0" />
        </linearGradient>
    </defs>
</svg>"""

    # 4. RTI Document
    document = f"""<svg width="60" height="80" viewBox="0 0 60 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="40" height="60" rx="4" fill="url(#grad3)" opacity="0.08"/>
    <rect x="10" y="10" width="40" height="60" rx="4" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.15"/>
    <line x1="20" y1="25" x2="30" y2="25" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.15"/>
    <line x1="20" y1="35" x2="40" y2="35" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.15"/>
    <line x1="20" y1="45" x2="40" y2="45" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.15"/>
    <line x1="20" y1="55" x2="35" y2="55" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.15"/>
    <defs>
        <linearGradient id="grad3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FFFFFF" stop-opacity="1" />
            <stop offset="100%" stop-color="#93C5FD" stop-opacity="0" />
        </linearGradient>
    </defs>
</svg>"""

    # 5. Public / Citizens (People icon)
    public = f"""<svg width="80" height="70" viewBox="0 0 80 70" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="25" r="12" fill="none" stroke="#60A5FA" stroke-width="3" opacity="0.15"/>
    <path d="M 20 60 C 20 45, 60 45, 60 60" fill="none" stroke="#60A5FA" stroke-width="3" stroke-linecap="round" opacity="0.15"/>
    <circle cx="20" cy="35" r="8" fill="none" stroke="#2563EB" stroke-width="2.5" opacity="0.12"/>
    <path d="M 5 65 C 5 55, 30 55, 30 65" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" opacity="0.12"/>
    <circle cx="60" cy="35" r="8" fill="none" stroke="#2563EB" stroke-width="2.5" opacity="0.12"/>
    <path d="M 50 65 C 50 55, 75 55, 75 65" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" opacity="0.12"/>
</svg>"""

    # 6. Shield (Protection / Rights)
    shield = f"""<svg width="70" height="80" viewBox="0 0 70 80" xmlns="http://www.w3.org/2000/svg">
    <path d="M 35 10 L 10 20 L 10 40 C 10 60, 35 70, 35 70 C 35 70, 60 60, 60 40 L 60 20 Z" fill="url(#grad4)" opacity="0.1"/>
    <path d="M 35 10 L 10 20 L 10 40 C 10 60, 35 70, 35 70 C 35 70, 60 60, 60 40 L 60 20 Z" fill="none" stroke="#2563EB" stroke-width="3" stroke-linejoin="round" opacity="0.15"/>
    <path d="M 25 40 L 32 47 L 45 30" fill="none" stroke="#2563EB" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.15"/>
    <defs>
        <linearGradient id="grad4" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2563EB" stop-opacity="1" />
            <stop offset="100%" stop-color="#60A5FA" stop-opacity="0" />
        </linearGradient>
    </defs>
</svg>"""

    # 7. Information / Search (Magnifying Glass over paper)
    info = f"""<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="15" y="15" width="35" height="45" rx="3" fill="none" stroke="#93C5FD" stroke-width="2.5" opacity="0.1"/>
    <circle cx="50" cy="50" r="14" fill="#0f172a" opacity="0.8"/> 
    <circle cx="50" cy="50" r="14" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.15"/>
    <line x1="60" y1="60" x2="70" y2="70" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.15"/>
</svg>"""
    
    # 8. Briefcase (Lawyer / Case file)
    briefcase = f"""<svg width="80" height="70" viewBox="0 0 80 70" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="25" width="60" height="40" rx="4" fill="none" stroke="#60A5FA" stroke-width="3" opacity="0.15"/>
    <path d="M 30 25 L 30 15 C 30 10, 50 10, 50 15 L 50 25" fill="none" stroke="#60A5FA" stroke-width="3" stroke-linecap="round" opacity="0.15"/>
    <line x1="10" y1="35" x2="70" y2="35" stroke="#60A5FA" stroke-width="3" opacity="0.15"/>
    <rect x="35" y="30" width="10" height="10" rx="2" fill="#60A5FA" opacity="0.12"/>
</svg>"""

    # 9. Stamp / Seal (Official Government approval)
    stamp = f"""<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="40" r="30" fill="none" stroke="#2563EB" stroke-width="2" stroke-dasharray="6,4" opacity="0.12"/>
    <circle cx="40" cy="40" r="22" fill="none" stroke="#2563EB" stroke-width="3" opacity="0.15"/>
    <path d="M 25 40 L 40 25 L 55 40 L 40 55 Z" fill="url(#grad5)" opacity="0.1"/>
    <path d="M 25 40 L 40 25 L 55 40 L 40 55 Z" fill="none" stroke="#2563EB" stroke-width="2" stroke-linejoin="round" opacity="0.12"/>
    <defs>
        <linearGradient id="grad5" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#2563EB" stop-opacity="1" />
            <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0" />
        </linearGradient>
    </defs>
</svg>"""

    # 10. Abstract Checkmark (Success / Verification)
    check = f"""<svg width="70" height="70" viewBox="0 0 70 70" xmlns="http://www.w3.org/2000/svg">
    <circle cx="35" cy="35" r="30" fill="url(#grad6)" opacity="0.08"/>
    <path d="M 20 35 L 30 45 L 50 25" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.15"/>
    <defs>
        <linearGradient id="grad6" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FFFFFF" stop-opacity="1" />
            <stop offset="100%" stop-color="#93C5FD" stop-opacity="0" />
        </linearGradient>
    </defs>
</svg>"""

    # Write individual SVGs
    assets = {
        'law_scales.svg': scales,
        'law_gavel.svg': gavel,
        'gov_pillar.svg': pillar,
        'rti_document.svg': document,
        'public_citizens.svg': public,
        'law_shield.svg': shield,
        'rti_search.svg': info,
        'law_briefcase.svg': briefcase,
        'gov_stamp.svg': stamp,
        'verification_check.svg': check
    }
    
    for name, content in assets.items():
        with open(os.path.join(out_dir, name), 'w') as f:
            f.write(content)

    print(f"Generated {len(assets)} legal/RTI SVG assets in {out_dir}")

    # Now create a combined HTML/SVG demo file that shows all these floating around
    demo_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Premium Floating RTI Doodles Demo</title>
<style>
    body {{
        margin: 0;
        padding: 0;
        background: #0f172a; /* Dark background to contrast the glassmorphism */
        overflow: hidden;
        font-family: system-ui, -apple-system, sans-serif;
    }}
    .glass-container {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 80%;
        max-width: 800px;
        height: 60%;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        z-index: 100;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }}
    .glass-content h1 {{
        font-weight: 300;
        letter-spacing: 2px;
        background: linear-gradient(to right, #93C5FD, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .floating-layer {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        overflow: hidden;
        z-index: 1;
    }}
    
    /* Animation Keyframes */
    @keyframes float-1 {{
        0% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
        33% {{ transform: translate(30px, -50px) rotate(3deg) scale(1.02); }}
        66% {{ transform: translate(-20px, 20px) rotate(-2deg) scale(0.98); }}
        100% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
    }}
    @keyframes float-2 {{
        0% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
        33% {{ transform: translate(-40px, 30px) rotate(-4deg) scale(0.99); }}
        66% {{ transform: translate(20px, -40px) rotate(2deg) scale(1.03); }}
        100% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
    }}
    @keyframes float-3 {{
        0% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
        33% {{ transform: translate(50px, 40px) rotate(3deg) scale(1.01); }}
        66% {{ transform: translate(-30px, -30px) rotate(-3deg) scale(0.99); }}
        100% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
    }}
    
    .doodle {{
        position: absolute;
    }}
</style>
</head>
<body>

    <div class="glass-container">
        <div class="glass-content">
            <h1>RTI ANALYSIS DASHBOARD</h1>
        </div>
    </div>

    <div class="floating-layer">
"""
    
    # Add instances of our SVGs to the demo
    random.seed(42) # For reproducibility
    
    for i in range(25):
        asset_name = random.choice(list(assets.keys()))
        asset_svg = assets[asset_name].replace('<svg ', '<svg width="100%" height="100%" ') # Strip width/height for inline
        
        # Randomize properties
        left = random.uniform(-10, 110)
        top = random.uniform(-10, 110)
        size = random.uniform(50, 200)
        
        anim = random.choice(['float-1', 'float-2', 'float-3'])
        duration = random.uniform(25, 45)
        delay = random.uniform(0, -45) # Negative delay to start at random points
        
        demo_html += f"""
        <div class="doodle" style="left: {left}%; top: {top}%; width: {size}px; height: {size}px; animation: {anim} {duration}s ease-in-out {delay}s infinite;">
            {asset_svg}
        </div>
        """

    demo_html += """
    </div>
</body>
</html>
"""

    with open(os.path.join(out_dir, 'demo.html'), 'w') as f:
        f.write(demo_html)
    print(f"Generated demo.html with legal/RTI icons")

if __name__ == '__main__':
    generate_svg_doodles()
