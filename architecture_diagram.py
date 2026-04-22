import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 18))
ax.set_xlim(0, 10)
ax.set_ylim(0, 18)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

# Title
ax.text(5, 17.3, 'Real-Time Multilingual Voice AI Agent', 
        fontsize=16, fontweight='bold', ha='center', va='center',
        color='#2c3e50')
ax.text(5, 16.8, 'Clinical Appointment Booking System', 
        fontsize=12, ha='center', va='center', color='#7f8c8d')

def draw_box(ax, x, y, w, h, text, color, textcolor='white', fontsize=10):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor='white',
                          linewidth=2, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, text, fontsize=fontsize, ha='center', va='center',
            color=textcolor, fontweight='bold', zorder=4)

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#95a5a6',
                               lw=2), zorder=2)

# Main pipeline boxes
boxes = [
    (5, 16.0, 4, 0.6, '🎤  User Voice Input', '#2ecc71'),
    (5, 14.8, 4, 0.6, '📝  Speech-to-Text (Google STT)', '#3498db'),
    (5, 13.6, 4, 0.6, '🌐  Language Detection', '#9b59b6'),
    (5, 12.4, 4, 0.6, '🧠  AI Agent (Groq / LLaMA 3.1)', '#e74c3c'),
    (5, 11.2, 4, 0.6, '🔧  Tool Orchestration', '#e67e22'),
    (5, 10.0, 4, 0.6, '📅  Appointment Service', '#1abc9c'),
    (5, 8.8,  4, 0.6, '💬  Text Response', '#3498db'),
    (5, 7.6,  4, 0.6, '🔊  Text-to-Speech (gTTS)', '#2ecc71'),
    (5, 6.4,  4, 0.6, '🎵  Audio Response to User', '#27ae60'),
]

for (x, y, w, h, text, color) in boxes:
    draw_box(ax, x, y, w, h, text, color)

# Arrows between main boxes
for i in range(len(boxes) - 1):
    draw_arrow(ax, boxes[i][0], boxes[i][1] - 0.3,
               boxes[i+1][0], boxes[i+1][1] + 0.3)

# Side boxes
# Memory
draw_box(ax, 1.5, 11.2, 2.2, 1.4, 'Memory\n📌 Session\n💾 Persistent', '#8e44ad', fontsize=9)
ax.annotate('', xy=(3.0, 11.2), xytext=(2.6, 11.2),
            arrowprops=dict(arrowstyle='<->', color='#8e44ad', lw=2))

# Database
draw_box(ax, 8.5, 10.0, 2.2, 1.4, 'Database\n🗄️ SQLite\nAppointments', '#16a085', fontsize=9)
ax.annotate('', xy=(7.0, 10.0), xytext=(7.4, 10.0),
            arrowprops=dict(arrowstyle='<->', color='#16a085', lw=2))

# Languages box
draw_box(ax, 5, 4.8, 6, 1.0, 
         '🌍  Languages: English  |  हिंदी Hindi  |  தமிழ் Tamil', 
         '#2c3e50', fontsize=10)

# WebSocket box
draw_box(ax, 5, 3.4, 6, 0.8, 
         '⚡  Real-Time WebSocket Communication', 
         '#c0392b', fontsize=10)

# Latency box
draw_box(ax, 5, 2.2, 6, 0.8,
         '⏱️  Target Latency: < 450ms  |  Measured & Logged',
         '#d35400', fontsize=10)

# Features box
ax.text(5, 1.2, 'Features: Book  •  Reschedule  •  Cancel  •  Conflict Detection  •  Outbound Campaigns',
        fontsize=9, ha='center', va='center', color='#2c3e50',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#ecf0f1', edgecolor='#bdc3c7'))

plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa')
print("Architecture diagram saved!")
plt.show()