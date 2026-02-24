"""Bio-Alpha Stress Tests — Adversarial scenarios.

7 scenarios: Capital Starvation, Drought, Heat Wave, pH Lockout,
CO2 Deprivation, Perfect Storm, 30-Day Runway.

Run:  python stress_test.py
Output: plots/07-09 + stress_results.txt
"""
import os, copy, math, random, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch
import pandas as pd
from bioalpha.simulation.engine import Model, Simulation
from bioalpha.simulation.model import (
    initial_state, state_update_blocks, params,
    p_environment, p_nutrients, p_growth,
    s_advance_time, s_update_day, s_update_light,
    s_update_humidity, s_update_vpd, s_update_biomass,
    s_update_growth_rate, s_update_health, s_update_economics,
    s_update_opex, s_count_co2, s_count_irrigation,
    s_count_mister, s_count_dosing,
)

PLOT_DIR = os.path.join(os.path.dirname(__file__), 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)
plt.rcParams.update({'figure.facecolor':'#0d1117','axes.facecolor':'#161b22','axes.edgecolor':'#30363d','axes.labelcolor':'#c9d1d9','text.color':'#c9d1d9','xtick.color':'#8b949e','ytick.color':'#8b949e','grid.color':'#21262d','grid.alpha':0.8,'font.size':11,'axes.titlesize':14,'axes.titleweight':'bold','figure.titlesize':16,'figure.titleweight':'bold','legend.facecolor':'#161b22','legend.edgecolor':'#30363d','legend.labelcolor':'#c9d1d9'})
C={'green':'#3fb950','blue':'#58a6ff','purple':'#bc8cff','orange':'#d29922','red':'#f85149','cyan':'#56d4dd','pink':'#f778ba','white':'#c9d1d9'}
dollar=FuncFormatter(lambda x,_:f'${x:,.0f}')
def save(fig,name): fig.savefig(os.path.join(PLOT_DIR,name),dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig); print(f'  Saved: plots/{name}')

def s_temp_heatwave(p,sub,sh,ps,pi): h=ps['hour_of_day']; d=3.0*math.sin(math.pi*(h-8)/12); led=2.5 if ps['light_is_on'] else 0; fan=pi.get('fan_pwm',0)/255*3; return ('temperature_c',round(35+d+led-fan+random.gauss(0,0.3),1))
def s_soil_drought(p,sub,sh,ps,pi): irr=25 if pi.get('fire_pump',False) else 0; return ('soil_moisture_pct',round(max(10,min(100,ps['soil_moisture_pct']-4.5+irr+random.gauss(0,0.5))),1))
def s_ph_lockout(p,sub,sh,ps,pi): cor=-0.3 if pi.get('dose_ph_down',False) else 0; return ('ph',round(max(4,min(9,ps['ph']+0.1+cor+random.gauss(0,0.02))),2))
def s_co2_deprived(p,sub,sh,ps,pi): b=350 if ps['light_is_on'] else 400; boost=50 if pi.get('fire_co2',False) else 0; return ('co2_ppm',max(300,min(600,b+boost+random.randint(-10,10))))
def s_temp_normal(p,sub,sh,ps,pi): h=ps['hour_of_day']; d=3*math.sin(math.pi*(h-8)/12); led=2.5 if ps['light_is_on'] else 0; fan=pi.get('fan_pwm',0)/255*3; return ('temperature_c',round(24+d+led-fan+random.gauss(0,0.3),1))
def s_soil_normal(p,sub,sh,ps,pi): irr=25 if pi.get('fire_pump',False) else 0; return ('soil_moisture_pct',round(max(10,min(100,ps['soil_moisture_pct']-1.5+irr+random.gauss(0,0.5))),1))
def s_ph_normal(p,sub,sh,ps,pi): cor=-0.3 if pi.get('dose_ph_down',False) else 0; return ('ph',round(max(4,min(9,ps['ph']+0.01+cor+random.gauss(0,0.02))),2))
def s_co2_normal(p,sub,sh,ps,pi): b=600 if ps['light_is_on'] else 900; boost=300 if pi.get('fire_co2',False) else 0; return ('co2_ppm',max(400,min(2000,b+boost+random.randint(-20,20))))
def s_tds_normal(p,sub,sh,ps,pi): boost=150 if pi.get('dose_nutrients',False) else 0; return ('tds_ppm',max(0,min(3000,int(ps['tds_ppm']-5+boost+random.randint(-5,5)))))

def build_blocks(tf,sf,phf,cf):
    return [{'policies':{'environment':p_environment,'nutrients':p_nutrients,'growth':p_growth},'variables':{'hour_of_day':s_advance_time,'day':s_update_day,'light_is_on':s_update_light,'temperature_c':tf,'humidity_pct':s_update_humidity,'vpd_kpa':s_update_vpd,'co2_ppm':cf,'soil_moisture_pct':sf,'ph':phf,'tds_ppm':s_tds_normal,'biomass_grams':s_update_biomass,'growth_rate':s_update_growth_rate,'health_score':s_update_health,'alpha_balance':s_update_economics,'total_opex':s_update_opex,'co2_bursts':s_count_co2,'irrigation_events':s_count_irrigation,'mister_events':s_count_mister,'dosing_events':s_count_dosing}}]

def run_scenario(label,custom_state=None,custom_blocks=None,custom_params=None,timesteps=168,runs=5):
    state={**initial_state,**(custom_state or {})}; blocks=custom_blocks or state_update_blocks; p={**params,**(custom_params or {})}
    model=Model(initial_state=state,state_update_blocks=blocks,params=p); sim=Simulation(model=model,timesteps=timesteps,runs=runs); df=pd.DataFrame(sim.run()); final=df[df['timestep']==df['timestep'].max()]
    print(f'\n  [{label}]'); print(f'    Biomass: {final["biomass_grams"].mean():.1f}g  Health: {final["health_score"].mean():.1f}  $ALPHA: ${final["alpha_balance"].mean():,.0f}  Survival: {(final["health_score"]>0).mean()*100:.0f}%')
    return df,final

def main():
    D7,D30=168,720; results={}
    print('='*60+'\nBIO-ALPHA STRESS TESTS\n'+'='*60)
    df0,f0=run_scenario('Baseline',timesteps=D7); results['Baseline']=(df0,f0)
    df1,f1=run_scenario('Capital Starvation',custom_state={'alpha_balance':5000},timesteps=D7); results['Capital\nStarvation']=(df1,f1)
    df2,f2=run_scenario('Drought',custom_blocks=build_blocks(s_temp_normal,s_soil_drought,s_ph_normal,s_co2_normal),timesteps=D7); results['Drought']=(df2,f2)
    df3,f3=run_scenario('Heat Wave',custom_blocks=build_blocks(s_temp_heatwave,s_soil_normal,s_ph_normal,s_co2_normal),timesteps=D7); results['Heat\nWave']=(df3,f3)
    df4,f4=run_scenario('pH Lockout',custom_blocks=build_blocks(s_temp_normal,s_soil_normal,s_ph_lockout,s_co2_normal),timesteps=D7); results['pH\nLockout']=(df4,f4)
    df5,f5=run_scenario('CO2 Deprivation',custom_blocks=build_blocks(s_temp_normal,s_soil_normal,s_ph_normal,s_co2_deprived),timesteps=D7); results['CO2\nDeprivation']=(df5,f5)
    df6,f6=run_scenario('Perfect Storm',custom_state={'alpha_balance':10000},custom_blocks=build_blocks(s_temp_heatwave,s_soil_drought,s_ph_lockout,s_co2_deprived),timesteps=D7); results['Perfect\nStorm']=(df6,f6)
    df7,f7=run_scenario('30-Day Runway',timesteps=D30,runs=3); results['30-Day\nRunway']=(df7,f7)
    print('\nGenerating stress test plots...')
    scenarios=['Baseline','Capital\nStarvation','Drought','Heat\nWave','pH\nLockout','CO2\nDeprivation','Perfect\nStorm']
    bc=[C['green'],C['orange'],C['blue'],C['red'],C['purple'],C['cyan'],C['pink']]; x=np.arange(len(scenarios)); w=0.6
    bio=[results[s][1]['biomass_grams'].mean() for s in scenarios]; health=[results[s][1]['health_score'].mean() for s in scenarios]; bal=[results[s][1]['alpha_balance'].mean() for s in scenarios]; surv=[(results[s][1]['health_score']>0).mean()*100 for s in scenarios]
    fig,axes=plt.subplots(2,2,figsize=(14,10)); fig.suptitle('Bio-Alpha STRESS TESTS',y=0.98)
    for i,(ax,vals,title,fmt) in enumerate([(axes[0,0],bio,'Final Biomass','g'),(axes[0,1],health,'Health Score',''),(axes[1,0],bal,'$ALPHA Remaining','$'),(axes[1,1],surv,'Survival Rate','%')]): ax.bar(x,vals,w,color=bc,alpha=0.85); ax.set_title(title); ax.set_xticks(x); ax.set_xticklabels(scenarios,fontsize=8); ax.grid(True,axis='y')
    if 1: axes[0,1].set_ylim(0,110); axes[0,1].axhline(y=50,color=C['red'],ls='--',alpha=0.5); axes[1,0].yaxis.set_major_formatter(dollar); axes[1,1].set_ylim(0,110)
    fig.tight_layout(rect=[0,0,1,0.95]); save(fig,'07_stress_test_dashboard.png')
    fig,axes=plt.subplots(2,3,figsize=(16,9)); fig.suptitle('Stress Test Time-Series',y=0.98)
    for label,df,color in [('Baseline',df0,C['green']),('Heat Wave',df3,C['red']),('pH Lockout',df4,C['purple']),('Perfect Storm',df6,C['pink'])]:
        d=df[(df['run']==1)&(df['timestep']>0)]; axes[0,0].plot(d['timestep'],d['biomass_grams'],label=label,color=color,lw=1.5,alpha=0.8); axes[0,1].plot(d['timestep'],d['health_score'],color=color,lw=1.5,alpha=0.8); axes[0,2].plot(d['timestep'],d['alpha_balance'],color=color,lw=1.5,alpha=0.8); axes[1,0].plot(d['timestep'],d['temperature_c'],color=color,lw=1,alpha=0.7); axes[1,1].plot(d['timestep'],d['soil_moisture_pct'],color=color,lw=1,alpha=0.7); axes[1,2].plot(d['timestep'],d['ph'],color=color,lw=1,alpha=0.7)
    axes[0,0].set_title('Biomass'); axes[0,0].legend(fontsize=8); axes[0,1].set_title('Health'); axes[0,1].set_ylim(0,110); axes[0,2].set_title('$ALPHA'); axes[0,2].yaxis.set_major_formatter(dollar)
    axes[1,0].set_title('Temperature'); axes[1,1].set_title('Soil Moisture'); axes[1,2].set_title('pH')
    for ax in axes.flat: ax.grid(True)
    fig.tight_layout(rect=[0,0,1,0.95]); save(fig,'08_stress_timeseries.png')
    fig,axes=plt.subplots(1,3,figsize=(15,5)); fig.suptitle('30-Day Runway Analysis',y=1.02)
    for r in df7['run'].unique(): d=df7[(df7['run']==r)&(df7['timestep']>0)]; axes[0].plot(d['timestep']/24,d['biomass_grams'],alpha=0.5,lw=1.2); axes[1].plot(d['timestep']/24,d['alpha_balance'],alpha=0.5,lw=1.2); axes[2].plot(d['timestep']/24,d['health_score'],alpha=0.5,lw=1.2)
    axes[0].set_title('Biomass'); axes[0].set_xlabel('Days'); axes[1].set_title('$ALPHA Runway'); axes[1].yaxis.set_major_formatter(dollar); axes[1].set_xlabel('Days'); axes[1].axhline(y=0,color=C['red'],ls='-',alpha=0.8,label='Liquidation'); axes[1].legend(fontsize=9); axes[2].set_title('Health'); axes[2].set_ylim(0,110); axes[2].set_xlabel('Days')
    for ax in axes: ax.grid(True)
    fig.tight_layout(); save(fig,'09_runway_30day.png')
    print('\n'+'='*80+'\nSUMMARY\n'+'='*80)
    for name in scenarios:
        f=results[name][1]; cn=name.replace('\n',' '); bio=f['biomass_grams'].mean(); h=f['health_score'].mean(); b=f['alpha_balance'].mean(); s=(f['health_score']>0).mean()*100
        v='DEAD' if h<=0 or s<50 else 'CRITICAL' if h<50 or b<=0 else 'DEGRADED' if h<80 or b<10000 else 'SURVIVED'
        print(f'  {cn:<18} | {bio:>5.1f}g | H:{h:>5.1f} | ${b:>9,.0f} | {s:>3.0f}% | {v}')

if __name__=='__main__': main()
