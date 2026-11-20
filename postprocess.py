import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm
from ipywidgets import fixed, widgets, interactive_output
import numpy as np
from IPython.display import display

def plot_velocity_field(nodes, connectivity, velocity_elems, scale_factor=5e8, skip=5):
    """
    Plot the velocity field as arrows on the mesh
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot mesh
    vnorm = (velocity_elems[:,0]**2 + velocity_elems[:,1]**2)**0.5
    ax.tripcolor(nodes[:,0], nodes[:,1], vnorm, triangles=connectivity, edgecolors='k', lw=0.2, alpha=0.3)
    
    # Interpolate velocities to nodes (simple averaging)
    velocity_nodes = np.zeros((len(nodes), 2))
    node_count = np.zeros(len(nodes))
    
    for i, elem in enumerate(connectivity):
        for node in elem:
            velocity_nodes[node] += velocity_elems[i]
            node_count[node] += 1
    
    # Average velocities at nodes
    for i in range(len(nodes)):
        if node_count[i] > 0:
            velocity_nodes[i] /= node_count[i]
    
    # Plot velocity vectors (subsample for clarity)
    skip = max(1, skip)
    X, Y = nodes[::skip, 0], nodes[::skip, 1]
    U, V = velocity_nodes[::skip, 0], velocity_nodes[::skip, 1]
    
    ax.quiver(X, Y, U*scale_factor, V*scale_factor, 
              angles='xy', scale_units='xy', scale=1, 
              color='red', alpha=0.7, lw=0.2, width=0.0012)
    
    ax.set_aspect('equal')
    ax.set_title('Groundwater Velocity Field')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    plt.axis('off')
    plt.tight_layout()

def plot_head_contours(nodes, connectivity, head):
    """
    Plot hydraulic head contours
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    tcf = ax.tricontourf(nodes[:,0], nodes[:,1], connectivity, head, levels=20, cmap='viridis')
    plt.colorbar(tcf, ax=ax, label='Hydraulic Head [m]')
    ax.set_aspect('equal')
    ax.set_title('Hydraulic Head Distribution')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    plt.axis('off')
    plt.tight_layout()
    return fig, ax

def plot_concentration(nodes, elements, results, step, critical_value=0.0001, highlight_nodes=[]):
    """
    Plot contaminant concentration at a given time step
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    x = nodes[:,0]
    y = nodes[:,1]
    cscale = colors.Normalize(min(results[step]), max(results[step]))
    tcf = ax.tricontourf(x, y, elements, results[step], norm=cscale, cmap=cm.coolwarm, levels=40)
    ax.tricontour(x, y, elements, results[step], colors='r', linewidths=1, levels=[critical_value])
    plt.colorbar(tcf, ax=ax, label='Concentration [kg/m$^3$]')
    ax.set_aspect('equal')
    ax.set_title(f'Contaminant concentration for time step {step}')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    for n in highlight_nodes:
        plt.plot(nodes[n,0],nodes[n,1],marker='x',color='white')
    plt.tight_layout()
    plt.axis('off')
    plt.show()

def plot_log_concentration(nodes, elements, results, step, highlight_nodes=[]):
    """
    Plot contaminant concentration at a given time step
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    x = nodes[:,0]
    y = nodes[:,1]
    truncated = np.maximum(results[step], 1e-16)
    vmax = -2
    vmin = -10
    tcf = ax.tricontourf(x, y, elements, np.log10(truncated), 
                         levels=np.linspace(vmin, vmax, 41),
                         norm=colors.Normalize(vmin, vmax), 
                         cmap=cm.coolwarm,
                         extend='both')
    plt.colorbar(tcf, ax=ax, label='log(Concentration) [kg/m$^3$]', extend='both')
    ax.set_aspect('equal')
    ax.set_title(f'Contaminant concentration for time step {step}')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    for n in highlight_nodes:
        plt.plot(nodes[n,0], nodes[n,1], marker='x', color='white')
    plt.tight_layout()
    plt.axis('off')
    plt.show()


def plot_concentration_interactive(nodes, elements, results, critical_value=0.0001, highlight_nodes=[]):
    nt = results.shape[0]
    play = widgets.Play(min=0, max=nt-1, step=1, value=0, interval=100, disabled=False)
    slider = widgets.IntSlider(min=0, max=nt-1, step=10, value=0)
    widgets.jslink((play, 'value'), (slider, 'value'))

    ui = widgets.HBox([play, slider])
    out = interactive_output(plot_concentration, 
                             {'step': slider, 
                              'nodes': fixed(nodes), 
                              'elements': fixed(elements), 
                              'results': fixed(results),
                              'critical_value': fixed(critical_value),
                              'highlight_nodes': fixed(highlight_nodes)
                              })

    display(ui, out)
