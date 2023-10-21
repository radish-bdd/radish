from rich import console, live
from time import sleep

c = console.Console()
c.status("[red]test[/red]")

lines = []

with live.Live() as lv:
    lv.update("Test")
    
    for i in range(32):
        
        if len(lines) > 0:
            lines.pop()
            lines.append(f'[green]{"*" * (i-1)}[/green]')
        lines.append(f'[yellow]{"*" * i}[/yellow]')
        lv.update('\n'.join(lines))
        sleep(.3)