"""
Phase E4 — Transitional Hotspot Parameter Sweeps.
Sorts systems by each descriptor and uses rolling windows to detect
curvature/possibility peaks — the locations of organizational transitions.
"""
import numpy as np, pandas as pd, os, json, time, warnings
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
OUT = '/home/student/sgp_core_v2/phases/phaseE'
df = pd.read_csv(os.path.join(OUT, 'phaseE_combined.csv'))
domains = sorted(df['domain'].unique())

cols_curvature = ['tangent_rotation','local_curvature','predictive_shear',
                  'geodesic_instab','jacobian_vol','desc_switch_vel']
cols_possibility = ['poss_reachable_volume','poss_branching_diversity',
                   'poss_adaptive_recovery','poss_future_entropy',
                   'poss_divergence_capacity','poss_stability_fertility_coupling']
cols_descriptors = ['CSR','RBS','ADI','RTP','SRD']

t_start = time.time()
print('='*70)
print('PHASE E4 — TRANSITIONAL HOTSPOTS')
print('='*70)

window = 20  # rolling window size
records = []

for domain in domains:
    m = df['domain'] == domain
    dm = df[m].reset_index(drop=True)
    
    for desc_col in cols_descriptors:
        # Sort by this descriptor
        sd = dm.sort_values(desc_col).reset_index(drop=True)
        
        for metric_col in cols_curvature + cols_possibility:
            vals = sd[metric_col].values
            
            # Rolling mean
            roll_mean = pd.Series(vals).rolling(window, center=True).mean().values
            # Peak detection: rolling mean above 75th percentile
            threshold = np.percentile(roll_mean[~np.isnan(roll_mean)], 75)
            
            for i in range(window//2, len(vals) - window//2):
                if np.isnan(roll_mean[i]): continue
                if roll_mean[i] > threshold:
                    # This is a hotspot
                    row = sd.iloc[i]
                    records.append({
                        'domain': domain,
                        'descriptor': desc_col,
                        'descriptor_value': row[desc_col],
                        'metric': metric_col,
                        'metric_value': row[metric_col],
                        'roll_mean': roll_mean[i],
                        'above_p75': True,
                        'sys_idx': row['sys_idx'],
                    })
    
    print(f'  {domain}: {len(records)} hotspot records → done')

hot_df = pd.DataFrame(records)
hot_path = os.path.join(OUT, 'phaseE4_transition_hotspots.csv')
hot_df.to_csv(hot_path, index=False)
print(f'\nE4 saved: {hot_path} ({len(hot_df)} rows)')

# Summary: which descriptor × metric pairs produce the most hotspots?
if len(hot_df) > 0:
    print('\n--- Hotspot density (records per descriptor-metric pair) ---')
    summary = hot_df.groupby(['descriptor','metric']).size().unstack(fill_value=0)
    print(summary)

    # Which descriptors yield the clearest hotspots?
    desc_intensity = hot_df.groupby('descriptor').size().sort_values(ascending=False)
    print('\n--- Hotspot count per descriptor ---')
    print(desc_intensity)

print(f'\nE4 COMPLETE ({time.time()-t_start:.0f}s)')
