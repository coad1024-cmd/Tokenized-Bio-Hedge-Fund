"""Bio-Alpha Experiment Plotter — Generates publication-quality charts.

Run:  python plot_experiments.py
Output: plots/ directory with 6 PNG files

Plots generated:
  01_baseline_timeseries.png  — 7-day time-series (6 subplots)
  02_monte_carlo_fan.png      — 5 Monte Carlo runs overlaid
  03_co2_cost_sweep.png       — CO2 cost sensitivity bars
  04_co2_ab_test.png          — Conservative vs Aggressive CO2
  05_light_ab_test.png        — 16h vs 20h light schedule
  06_roi_summary.png          — Strategy ROI comparison

Requires: matplotlib, numpy, pandas
"""
import os, math, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch
from bioalpha.simulation.model import run_simulation, run_parameter_sweep, run_ab_test

SEVEN_DAYS = 168
PLOT_DIR = os.path.join(os.path.dirname(__file__), 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

plt.rcParams.update({'figure.facecolor':'#0d1117','axes.facecolor':'#161b22','axes.edgecolor':'#30363d','axes.labelcolor':'#c9d1d9','text.color':'#c9d1d9','xtick.color':'#8b949e','ytick.color':'#8b949e','grid.color':'#21262d','grid.alpha':0.8,'font.family':'sans-serif','font.size':11,'axes.titlesize':14,'axes.titleweight':'bold','figure.titlesize':16,'figure.titleweight':'bold','legend.facecolor':'#161b22','legend.edgecolor':'#30363d','legend.labelcolor':'#c9d1d9'})
C = {'green':'#3fb950','blue':'#58a6ff','purple':'#bc8cff','orange':'#d29922','red':'#f85149','cyan':'#56d4dd','pink':'#f778ba','white':'#c9d1d9'}
dollar = FuncFormatter(lambda x,_: f'${x:,.0f}')
def save(fig,name): fig.savefig(os.path.join(PLOT_DIR,name),dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig); print(f'  Saved: plots/{name}')

def plot_baseline():
    print('Plot 1: Baseline 7-day time-series...')
    df=run_simulation(timesteps=SEVEN_DAYS,runs=1); df=df[df['timestep']>0]; t=df['timestep'].values
    fig,axes=plt.subplots(3,2,figsize=(14,10)); fig.suptitle('Bio-Alpha Baseline Simulation \u2014 7 Days (Hourly)',y=0.98)
    ax=axes[0,0]; ax.plot(t,df['biomass_grams'],color=C['green'],lw=2); ax.set_ylabel('Biomass (g)'); ax.set_title('Plant Growth'); ax.fill_between(t,0,df['biomass_grams'],alpha=0.15,color=C['green']); ax.grid(True)
    ax=axes[0,1]; ax.plot(t,df['alpha_balance'],color=C['orange'],lw=2); ax.set_ylabel('$ALPHA'); ax.set_title('Fund Balance'); ax.yaxis.set_major_formatter(dollar); ax.grid(True)
    ax=axes[1,0]; ax.plot(t,df['temperature_c'],color=C['red'],lw=1.2,label='Temp'); ax2=ax.twinx(); ax2.plot(t,df['co2_ppm'],color=C['cyan'],lw=1.2,alpha=0.7); ax.set_ylabel('Temperature (\u00b0C)',color=C['red']); ax2.set_ylabel('CO2 (ppm)',color=C['cyan']); ax.set_title('Temperature & CO2'); ax.grid(True)
    ax=axes[1,1]; ax.plot(t,df['soil_moisture_pct'],color=C['blue'],lw=1.5); ax2=ax.twinx(); ax2.plot(t,df['ph'],color=C['purple'],lw=1.2,alpha=0.8); ax.set_ylabel('Soil Moisture (%)',color=C['blue']); ax2.set_ylabel('pH',color=C['purple']); ax.set_title('Soil Moisture & pH'); ax.grid(True)
    ax=axes[2,0]; ax.plot(t,df['health_score'],color=C['pink'],lw=2); ax.set_ylabel('Health Score'); ax.set_title('Plant Health'); ax.set_ylim(0,110); ax.set_xlabel('Hours'); ax.grid(True)
    ax=axes[2,1]; ax.plot(t,df['tds_ppm'],color=C['purple'],lw=1.5); ax.set_ylabel('TDS (ppm)'); ax.set_title('Nutrient Concentration'); ax.set_xlabel('Hours'); ax.grid(True)
    fig.tight_layout(rect=[0,0,1,0.95]); save(fig,'01_baseline_timeseries.png')

def plot_monte_carlo():
    print('Plot 2: Monte Carlo fan chart (5 runs)...')
    df=run_simulation(timesteps=SEVEN_DAYS,runs=5); df=df[df['timestep']>0]
    fig,axes=plt.subplots(1,3,figsize=(15,5)); fig.suptitle('Monte Carlo Simulation \u2014 5 Runs Overlaid',y=1.02)
    for r in df['run'].unique():
        rd=df[df['run']==r]; t=rd['timestep'].values
        axes[0].plot(t,rd['biomass_grams'],alpha=0.6,lw=1.5); axes[1].plot(t,rd['alpha_balance'],alpha=0.6,lw=1.5); axes[2].plot(t,rd['health_score'],alpha=0.6,lw=1.5)
    axes[0].set_title('Biomass Growth'); axes[0].set_ylabel('Grams'); axes[0].set_xlabel('Hours'); axes[0].grid(True)
    axes[1].set_title('$ALPHA Balance'); axes[1].yaxis.set_major_formatter(dollar); axes[1].set_xlabel('Hours'); axes[1].grid(True)
    axes[2].set_title('Health Score'); axes[2].set_ylim(0,110); axes[2].set_xlabel('Hours'); axes[2].grid(True)
    fig.tight_layout(); save(fig,'02_monte_carlo_fan.png')

def plot_co2_sweep():
    print('Plot 3: CO2 cost sensitivity sweep...')
    df=run_parameter_sweep(sweep_params={'co2_cost':[5,10,20,40]},timesteps=SEVEN_DAYS,runs_per_config=3)
    final=df[df['timestep']==df['timestep'].max()]; costs=[5,10,20,40]; labels=['$5','$10','$20','$40']
    biomass=[final[final['subset']==i]['biomass_grams'].mean() for i in range(4)]
    balance=[final[final['subset']==i]['alpha_balance'].mean() for i in range(4)]
    opex=[final[final['subset']==i]['total_opex'].mean() for i in range(4)]
    fig,axes=plt.subplots(1,3,figsize=(14,5)); fig.suptitle('Experiment 1: CO2 Cost Sensitivity Sweep',y=1.02); x=np.arange(4); w=0.5
    axes[0].bar(x,biomass,w,color=C['green'],alpha=0.85); axes[0].set_title('Final Biomass'); axes[0].set_ylabel('Grams'); axes[0].set_xticks(x); axes[0].set_xticklabels(labels); axes[0].set_xlabel('CO2 Cost/Burst'); axes[0].grid(True,axis='y')
    for i,v in enumerate(biomass): axes[0].text(i,v+0.05,f'{v:.1f}g',ha='center',fontsize=10,color=C['white'])
    axes[1].bar(x,balance,w,color=C['orange'],alpha=0.85); axes[1].set_title('$ALPHA Remaining'); axes[1].yaxis.set_major_formatter(dollar); axes[1].set_xticks(x); axes[1].set_xticklabels(labels); axes[1].set_xlabel('CO2 Cost/Burst'); axes[1].grid(True,axis='y')
    axes[2].bar(x,opex,w,color=C['red'],alpha=0.85); axes[2].set_title('Total OPEX'); axes[2].yaxis.set_major_formatter(dollar); axes[2].set_xticks(x); axes[2].set_xticklabels(labels); axes[2].set_xlabel('CO2 Cost/Burst'); axes[2].grid(True,axis='y')
    fig.tight_layout(); save(fig,'03_co2_cost_sweep.png')

def plot_co2_ab():
    print('Plot 4: Conservative vs Aggressive CO2...')
    df_a,df_b=run_ab_test(params_a={'co2_min':[600]},params_b={'co2_min':[1000]},timesteps=SEVEN_DAYS,runs=5)
    fig,axes=plt.subplots(1,3,figsize=(15,5)); fig.suptitle('Experiment 2: Conservative (600ppm) vs Aggressive (1000ppm) CO2',y=1.02)
    for r in df_a['run'].unique():
        rd=df_a[(df_a['run']==r)&(df_a['timestep']>0)]; axes[0].plot(rd['timestep'],rd['biomass_grams'],color=C['blue'],alpha=0.4,lw=1); axes[1].plot(rd['timestep'],rd['alpha_balance'],color=C['blue'],alpha=0.4,lw=1); axes[2].plot(rd['timestep'],rd['co2_ppm'],color=C['blue'],alpha=0.4,lw=1)
    for r in df_b['run'].unique():
        rd=df_b[(df_b['run']==r)&(df_b['timestep']>0)]; axes[0].plot(rd['timestep'],rd['biomass_grams'],color=C['red'],alpha=0.4,lw=1); axes[1].plot(rd['timestep'],rd['alpha_balance'],color=C['red'],alpha=0.4,lw=1); axes[2].plot(rd['timestep'],rd['co2_ppm'],color=C['red'],alpha=0.4,lw=1)
    lg=[Patch(color=C['blue'],label='Conservative (600ppm)'),Patch(color=C['red'],label='Aggressive (1000ppm)')]
    axes[0].set_title('Biomass Growth'); axes[0].set_ylabel('Grams'); axes[0].set_xlabel('Hours'); axes[0].legend(handles=lg,loc='upper left',fontsize=9); axes[0].grid(True)
    axes[1].set_title('$ALPHA Balance'); axes[1].yaxis.set_major_formatter(dollar); axes[1].set_xlabel('Hours'); axes[1].grid(True)
    axes[2].set_title('CO2 Levels'); axes[2].set_ylabel('ppm'); axes[2].set_xlabel('Hours'); axes[2].grid(True)
    fig.tight_layout(); save(fig,'04_co2_ab_test.png')

def plot_light_ab():
    print('Plot 5: 16h vs 20h light...')
    df_a,df_b=run_ab_test(params_a={'light_on_hour':[6],'light_off_hour':[22]},params_b={'light_on_hour':[4],'light_off_hour':[24]},timesteps=SEVEN_DAYS,runs=5)
    fig,axes=plt.subplots(1,3,figsize=(15,5)); fig.suptitle('Experiment 3: 16h vs 20h Light Schedule',y=1.02)
    for r in df_a['run'].unique():
        rd=df_a[(df_a['run']==r)&(df_a['timestep']>0)]; axes[0].plot(rd['timestep'],rd['biomass_grams'],color=C['orange'],alpha=0.4,lw=1); axes[1].plot(rd['timestep'],rd['alpha_balance'],color=C['orange'],alpha=0.4,lw=1)
    for r in df_b['run'].unique():
        rd=df_b[(df_b['run']==r)&(df_b['timestep']>0)]; axes[0].plot(rd['timestep'],rd['biomass_grams'],color=C['cyan'],alpha=0.4,lw=1); axes[1].plot(rd['timestep'],rd['alpha_balance'],color=C['cyan'],alpha=0.4,lw=1)
    lg=[Patch(color=C['orange'],label='16h (6AM-10PM)'),Patch(color=C['cyan'],label='20h (4AM-12AM)')]
    axes[0].set_title('Biomass Growth'); axes[0].set_ylabel('Grams'); axes[0].set_xlabel('Hours'); axes[0].legend(handles=lg,loc='upper left',fontsize=9); axes[0].grid(True)
    axes[1].set_title('$ALPHA Balance'); axes[1].yaxis.set_major_formatter(dollar); axes[1].set_xlabel('Hours'); axes[1].grid(True)
    fa=df_a[df_a['timestep']==df_a['timestep'].max()]; fb=df_b[df_b['timestep']==df_b['timestep'].max()]; w=0.3
    axes[2].bar(0-w/2,fa['biomass_grams'].mean(),w,color=C['orange'],label='16h'); axes[2].bar(0+w/2,fb['biomass_grams'].mean(),w,color=C['cyan'],label='20h')
    axes[2].bar(1-w/2,fa['co2_bursts'].mean(),w,color=C['orange']); axes[2].bar(1+w/2,fb['co2_bursts'].mean(),w,color=C['cyan'])
    axes[2].bar(2-w/2,fa['irrigation_events'].mean(),w,color=C['orange']); axes[2].bar(2+w/2,fb['irrigation_events'].mean(),w,color=C['cyan'])
    axes[2].set_xticks([0,1,2]); axes[2].set_xticklabels(['Biomass (g)','CO2 Bursts','Irrigations']); axes[2].set_title('Strategy Comparison'); axes[2].legend(fontsize=9); axes[2].grid(True,axis='y')
    fig.tight_layout(); save(fig,'05_light_ab_test.png')

def plot_roi_summary():
    print('Plot 6: ROI summary...')
    strats={'Baseline\n(16h, 800ppm)':{'light_on_hour':[6],'light_off_hour':[22],'co2_min':[800]},'Aggressive CO2\n(16h, 1000ppm)':{'light_on_hour':[6],'light_off_hour':[22],'co2_min':[1000]},'Extended Light\n(20h, 800ppm)':{'light_on_hour':[4],'light_off_hour':[24],'co2_min':[800]},'Max Growth\n(20h, 1000ppm)':{'light_on_hour':[4],'light_off_hour':[24],'co2_min':[1000]}}
    names,biomasses,opexes,rois=[],[],[],[]
    for name,p in strats.items():
        df=run_parameter_sweep(sweep_params=p,timesteps=SEVEN_DAYS,runs_per_config=3); final=df[df['timestep']==df['timestep'].max()]
        bio=final['biomass_grams'].mean(); opex=final['total_opex'].mean(); roi=bio/opex*1000 if opex>0 else 0
        names.append(name); biomasses.append(bio); opexes.append(opex); rois.append(roi)
    fig,axes=plt.subplots(1,3,figsize=(15,5.5)); fig.suptitle('Strategy Comparison \u2014 Return on Investment',y=1.02)
    x=np.arange(4); w=0.5; bc=[C['blue'],C['red'],C['cyan'],C['green']]
    axes[0].bar(x,biomasses,w,color=bc,alpha=0.85); axes[0].set_title('Final Biomass'); axes[0].set_ylabel('Grams'); axes[0].set_xticks(x); axes[0].set_xticklabels(names,fontsize=8); axes[0].grid(True,axis='y')
    for i,v in enumerate(biomasses): axes[0].text(i,v+0.1,f'{v:.1f}g',ha='center',fontsize=9,color=C['white'])
    axes[1].bar(x,opexes,w,color=bc,alpha=0.85); axes[1].set_title('Total OPEX (7 days)'); axes[1].set_ylabel('$ALPHA Spent'); axes[1].yaxis.set_major_formatter(dollar); axes[1].set_xticks(x); axes[1].set_xticklabels(names,fontsize=8); axes[1].grid(True,axis='y')
    axes[2].bar(x,rois,w,color=bc,alpha=0.85); axes[2].set_title('Biomass ROI (g per 1K $ALPHA)'); axes[2].set_ylabel('g / 1000 $ALPHA'); axes[2].set_xticks(x); axes[2].set_xticklabels(names,fontsize=8); axes[2].grid(True,axis='y')
    for i,v in enumerate(rois): axes[2].text(i,v+0.01,f'{v:.2f}',ha='center',fontsize=9,color=C['white'])
    fig.tight_layout(); save(fig,'06_roi_summary.png')

if __name__=='__main__':
    print('='*60+'\nBio-Alpha Experiment Plotter\n'+'='*60)
    plot_baseline(); plot_monte_carlo(); plot_co2_sweep(); plot_co2_ab(); plot_light_ab(); plot_roi_summary()
    print(f'\nAll plots saved to: {PLOT_DIR}/\n'+'='*60)
