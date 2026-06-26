ICON='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>'
def edit(path, repls):
    s=open(path,encoding="utf-8").read(); applied=[]
    for old,new in repls:
        if old in s: s=s.replace(old,new,1); applied.append(True)
        else: applied.append(False)
    open(path,"w",encoding="utf-8").write(s); return applied

# 1) shipping line: nad / sermorelin / glutathione
ship_old='<h4>Free expedited shipping</h4><p>Discreet packaging, delivered to your door. Cold-chain shipping when required.'
ship_new='<h4>Free expedited cold-chain shipping</h4><p>Discreet packaging, delivered to your door.'
for p in ["nad.html","sermorelin.html","glutathione.html"]:
    print(p, "shipping:", edit(p,[(ship_old,ship_new)]))

# 2) NAD vial feature: add weekly dosing (vial size flagged separately to Orlando)
print("nad vial dosing:", edit("nad.html",[(
 '<h4>NAD+ injection vial</h4><p>Pharmaceutical-grade nicotinamide adenine dinucleotide. Subcutaneous injection for rapid absorption.</p>',
 '<h4>NAD+ injection vial</h4><p>Pharmaceutical-grade nicotinamide adenine dinucleotide. Subcutaneous injection for rapid absorption. Dosed 2-3 times per week per your provider.</p>'
)]))

# 3) MICC: add cold-chain shipping item after Ongoing care
micc_old='<div><h4>Ongoing care</h4><p>Dose adjustment, side effect management, paired with GLP-1, your provider is one message away.</p></div></div>'
micc_new='<div><h4>Ongoing care</h4><p>Dose adjustment, side effect management, paired with GLP-1, your provider is one message away.</p></div></div>'+\
 f'<div class="included-item"><div class="icon">{ICON}</div><div><h4>Free expedited cold-chain shipping</h4><p>Discreet, temperature-controlled packaging, delivered to your door.</p></div></div>'
print("micc cold-chain:", edit("micc.html",[(micc_old,micc_new)]))

# 4) antiparasitic.html coverage box
anti=[
 ("Compounded ivermectin, dosed by your provider","Compounded ivermectin"),
 ("30-day supply, refilled on schedule","30-day, 60-day, &amp; 90 day options"),
 ("<strong>Two</strong> antiparasitics, ivermectin + mebendazole","<strong>Two</strong> antiparasitics, Ivermectin + Mebendazole"),
 ("Both compounded to your dose by a U.S. pharmacy","Compounded by a U.S. pharmacy"),
 (f"30-day supply, discreet 2-day shipping, cancel anytime</li>", f"30-day, 60-day, &amp; 90 day options</li><li>{ICON}Monthly Plan, cancel anytime</li>"),
 (">Check eligibility <svg",">Start your consultation <svg"),  # button 1
]
res=edit("antiparasitic.html",anti)
# second button (same string again)
res2=edit("antiparasitic.html",[(">Check eligibility <svg",">Start your consultation <svg")])
print("antiparasitic box:", res, "btn2:", res2)
