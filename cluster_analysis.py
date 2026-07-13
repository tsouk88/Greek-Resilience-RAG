import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from adjustText import adjust_text  

# Raw data from findings.md
data = {
    'Region': [
        'ΑΜΘ', 'Κεντρική Μακεδονία', 'Δυτική Μακεδονία', 'Ήπειρος',
        'Θεσσαλία', 'Ιόνια Νησιά', 'Δυτική Ελλάδα', 'Στερεά Ελλάδα',
        'Αττική', 'Πελοπόννησος', 'Βόρειο Αιγαίο', 'Νότιο Αιγαίο', 'Κρήτη'
    ],
    'Econ_Rs': [-3.533, -4.436, -1.913, -2.991, -4.498, -3.483, -4.264, -4.196, -7.888, -3.460, -3.273, -3.287, -4.374],
    'Econ_Rc': [0.771, 0.917, -0.328, 0.650, 0.726, 2.470, 0.696, 0.541, 1.469, 0.893, -0.466, 1.904, 1.541],
    'Econ_D':  [0.385, 0.850, 1.023, 1.351, 1.077, 4.633, 0.926, -0.067, 0.999, 2.256, 0.075, 2.597, 1.369],
    'Soc_Rs':  [-1.385, -3.651, 0.097, -1.393, -0.645, -0.074, -1.988, -0.524, -5.966, -0.635, 0.856, -0.236, -0.443],
    'Soc_Rc':  [0.174, 0.277, -0.729, -1.245, -1.011, 2.029, 2.085, -0.345, 3.061, -0.994, 1.550, 0.546, 0.289],
    'Soc_D':   [9.064, 5.811, 9.387, 9.899, 10.565, 9.075, 9.846, 7.957, 6.304, 8.941, 14.393, 9.275, 9.832],
}

df = pd.DataFrame(data)

# Combined features
df['Avg_Rs'] = (df['Econ_Rs'] + df['Soc_Rs']) / 2
df['Avg_Rc'] = (df['Econ_Rc'] + df['Soc_Rc']) / 2
df['Avg_D']  = (df['Econ_D']  + df['Soc_D'])  / 2

features = df[['Avg_Rs', 'Avg_Rc', 'Avg_D']].values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Find optimal k
sil_scores = {}
for k in range(2, 6):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(features_scaled)
    sil_scores[k] = silhouette_score(features_scaled, labels)
    print(f"k={k}: silhouette={sil_scores[k]:.3f}")

best_k = 4 
print(f"\nBest k: {best_k}")

km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df['Cluster'] = km_final.fit_predict(features_scaled)

# Name clusters based on characteristics
cluster_means = df.groupby('Cluster')[['Avg_Rs', 'Avg_Rc', 'Avg_D']].mean()
print("\nCluster means:")
print(cluster_means)
print("\nRegions per cluster:")
for c in sorted(df['Cluster'].unique()):
    regions = df[df['Cluster'] == c]['Region'].tolist()
    print(f"Cluster {c}: {regions}")

cluster_names = {
    0: "Δομική\nΣτασιμότητα",
    1: "Τουριστικός\nΜετασχηματισμός",
    2: "Αναδυόμενη\nΠροσαρμογή",
    3: "Μητροπολιτικό\nΠαράδοξο"
}

# Assign names based on D score (highest D = most transformative)
cluster_d_rank = cluster_means['Avg_D'].rank(ascending=False)
cluster_names = {
    0: "Δομική\nΣτασιμότητα",
    1: "Τουριστικός\nΜετασχηματισμός",
    2: "Αναδυόμενη\nΠροσαρμογή",
    3: "Μητροπολιτικό\nΠαράδοξο"
}

df['Cluster_Name'] = df['Cluster'].map(cluster_names)

# ── FIGURE 1: Scatter Rs vs D ────────────────────────────────────────────────
colors = ['#2e6da4', '#e8a020', '#27ae60', '#8e44ad']
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#0f2035')

ax1 = axes[0]
ax1.set_facecolor('#1a3a5c')
for c in sorted(df['Cluster'].unique()):
    subset = df[df['Cluster'] == c]
    ax1.scatter(subset['Avg_Rs'], subset['Avg_D'],
                color=colors[c], s=120, zorder=5, label=cluster_names[c])
    for _, row in subset.iterrows():
        ax1.annotate(row['Region'], (row['Avg_Rs'], row['Avg_D']),
                     textcoords="offset points", xytext=(6, 4),
                     fontsize=8, color='white')

ax1.axhline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.4)
ax1.axvline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.4)
ax1.set_xlabel('Αντίσταση (Rs)', color='white', fontsize=11)
ax1.set_ylabel('Τροχιακή Απόκλιση (D)', color='white', fontsize=11)
ax1.set_title('Αντίσταση vs Τροχιακή Απόκλιση', color='white', fontsize=13, pad=12)
ax1.tick_params(colors='white')
ax1.spines[:].set_color('#2e6da4')
legend = ax1.legend(fontsize=8, facecolor='#1a3a5c', labelcolor='white', 
                     edgecolor='#2e6da4', loc='upper right')

# ── FIGURE 2: Scatter Rc vs D ────────────────────────────────────────────────
ax2 = axes[1]
ax2.set_facecolor('#1a3a5c')
for c in sorted(df['Cluster'].unique()):
    subset = df[df['Cluster'] == c]
    ax2.scatter(subset['Avg_Rc'], subset['Avg_D'],
                color=colors[c], s=120, zorder=5, label=cluster_names[c])
    for _, row in subset.iterrows():
        ax2.annotate(row['Region'], (row['Avg_Rc'], row['Avg_D']),
                     textcoords="offset points", xytext=(6, 4),
                     fontsize=8, color='white')

ax2.axhline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.4)
ax2.axvline(0, color='white', linewidth=0.5, linestyle='--', alpha=0.4)
ax2.set_xlabel('Ανάκαμψη (Rc)', color='white', fontsize=11)
ax2.set_ylabel('Τροχιακή Απόκλιση (D)', color='white', fontsize=11)
ax2.set_title('Ανάκαμψη vs Τροχιακή Απόκλιση', color='white', fontsize=13, pad=12)
ax2.tick_params(colors='white')
ax2.spines[:].set_color('#2e6da4')
ax2.legend(fontsize=8, facecolor='#1a3a5c', labelcolor='white',
           edgecolor='#2e6da4', loc='upper left')

fig.suptitle('Χωρική Ανάλυση Clusters — Ελληνικές Περιφέρειες', 
             color='white', fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('cluster_scatter.png', dpi=150, bbox_inches='tight',
            facecolor='#0f2035')
print("Saved cluster_scatter.png")

# ── FIGURE 3: Radar Chart per Cluster ───────────────────────────────────────
categories = ['Αντίσταση\n(Rs)', 'Ανάκαμψη\n(Rc)', 'Τροχιακή\nΑπόκλιση (D)']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

fig2, axes2 = plt.subplots(1, best_k, figsize=(5*best_k, 5),
                            subplot_kw=dict(polar=True))
fig2.patch.set_facecolor('#0f2035')

if best_k == 1:
    axes2 = [axes2]

cluster_means_raw = df.groupby('Cluster')[['Avg_Rs', 'Avg_Rc', 'Avg_D']].mean()

for idx, c in enumerate(sorted(df['Cluster'].unique())):
    ax = axes2[idx]
    ax.set_facecolor('#1a3a5c')
    
    vals_raw = cluster_means_raw.loc[c].values.tolist()
    
    # Global min/max across ALL clusters για consistent normalization
    global_min = cluster_means_raw.values.min(axis=0)
    global_max = cluster_means_raw.values.max(axis=0)
    ranges = global_max - global_min
    ranges[ranges == 0] = 1
    
    # Normalize 0-1
    vals_norm = [(v - global_min[i]) / ranges[i] for i, v in enumerate(vals_raw)]
    vals_norm += vals_norm[:1]
    
    ax.plot(angles, vals_norm, color=colors[c], linewidth=2)
    ax.fill(angles, vals_norm, color=colors[c], alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color='white', fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels(['Low', 'Mid', 'High'], color='#7ab8e8', fontsize=7)
    ax.spines['polar'].set_color('#2e6da4')
    ax.grid(color='#2e6da4', alpha=0.4)
    
    regions = df[df['Cluster'] == c]['Region'].tolist()
    
    if len(regions) == 1:
        ax.set_title(f"{cluster_names[c]}\n(Αττική — Μοναδικός Outlier)\nRs=-6.93 | Rc=2.27 | D=3.65",
                     color='white', fontsize=9, pad=15)
        ax.text(0, 0, "OUTLIER", ha='center', va='center',
                color=colors[c], fontsize=14, fontweight='bold')
    else:
        ax.set_title(f"{cluster_names[c]}\n({', '.join(regions)})",
                     color='white', fontsize=9, pad=15)

fig2.suptitle('Radar Charts ανά Cluster — RTIx Συνιστώσες',
              color='white', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('cluster_radar.png', dpi=150, bbox_inches='tight',
            facecolor='#0f2035')
print("Saved cluster_radar.png")
plt.close('all')
print("\nDone! Check cluster_scatter.png and cluster_radar.png")