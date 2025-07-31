from graphviz import Digraph
import io

def generate_diagram_image(prompt: str) -> bytes:
    # Simple example for demo - customize further per need
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')
    dot.attr('node', shape='box', style='filled', color='lightblue', fontname='Helvetica')

    dot.node('Start', 'Start')
    dot.node('Step1', 'Receive Order')
    dot.node('Step2', 'Verify Inventory')
    dot.node('Step3', 'Pick & Pack')
    dot.node('Step4', 'Dispatch')
    dot.node('End', 'End')

    dot.edges(['StartStep1', 'Step1Step2', 'Step2Step3', 'Step3Step4', 'Step4End'])

    # Output image as bytes
    img_bytes = dot.pipe(format='png')
    return img_bytes
