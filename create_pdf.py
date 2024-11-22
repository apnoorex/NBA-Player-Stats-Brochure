import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os


# Parameters of the brochure
text_color = (105,105,105)
graph_text_color = '#808080'
stats_graph_color = '#658585'
earnings_graph_color = '#677e84'
linewidth = 1.4

def create_img(model, fig):
    fig.savefig('tmp.png')
    model.image('tmp.png', x=5, h=20)
    os.remove('tmp.png')

def set_graph_parameters(ax, title_str):
    ax.spines['bottom'].set_color(graph_text_color)
    ax.spines['top'].set_color('#ffffff') 
    ax.spines['right'].set_color('#ffffff')
    ax.spines['left'].set_color(graph_text_color)
    ax.tick_params(axis='x', colors=graph_text_color)
    ax.tick_params(axis='y', colors=graph_text_color)
    plt.title(title_str, x=0.9, y=0.9, fontsize=8, font='Noto Sans', color='#808080')

def print_stats_graph(x, y, model, title_str):
    fig, ax = plt.subplots(figsize=(11, 2))
    plt.plot(x, y, color=stats_graph_color, linewidth=linewidth)
    set_graph_parameters(ax, title_str)
    create_img(model, fig)

def print_line(model, y_space, x_space, text, size, style):
    model.set_font('helvetica', style=style, size=size)
    model.set_text_color(text_color)
    model.ln(y_space)
    model.cell(x_space)
    model.cell(text=text, new_y=YPos.NEXT)    

def get_info(player):
    filename = f"out_data/{player.replace(' ', '_')}.txt"
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

def create_pdf(player):
    class PDF(FPDF):
        """ Creating a footer for the brochure. """
        def footer(self):
            self.set_y(-15.5)
            self.set_x(-90)
            self.set_font('Helvetica', 'I', 5)
            self.set_text_color(200, 200, 200)
            self.cell(0, 10, text="Data courtesy of Spotrac.com. Team logo downloaded from ESPN.com. Created by apnoorex")
            self.cell(10)
            self.image('in_data/qrcode/qr_code.png', x=113, y=203.8, h=5)

    # Import data
    player_info = get_info(player)

    filename = f"out_data/{player.replace(' ', '_')}.csv"
    stats = pd.read_csv(filename)

    # Variables
    current_team = player_info[0].split(',')[0].split(':')[-1]
    first_year = stats['Year'][0]
    last_year = stats['Year'].iloc[-1]
    earnings = [int(s.replace('$', '').replace(',', '')) for s in list(stats['BaseSalary'])]
    points = [float(s) for s in list(stats['Pt/Gm'])]
    assists = [float(s) for s in list(stats['Ast/Gm'])]
    rebounds = [float(s) for s in list(stats['Reb/Gm'])]
    years = [str(s) for s in list(stats['Year'])]

    # Create a blank PDF page
    pdf = PDF('P', 'mm', format=(124, 215))
    pdf.add_page()

    # Add logo
    pdf.image(f"in_data/logos/{player_info[-2]}.png", x=12, y=12, h=40)

    # First name
    print_line(pdf, 6, 52, player.split()[0], 16, 'B')
    # Last name
    print_line(pdf, 2, 52, player.split()[1], 22, 'B')
    # Position
    print_line(pdf, 6, 52, 'Position:' + str(player_info[0].split(',')[-1]), 8, '')
    # Country
    print_line(pdf, 1.5, 52, player_info[2], 8, '')
    # Experience
    print_line(pdf, 1.5, 52, player_info[1], 8, '')
    # Draft info
    print_line(pdf, 1.5, 52, player_info[3], 8, '')

    # Information block is different for retired and active players
    if player_info[-1] == 'True':
        about_1 = f"{player.split()[0]} has earned ${sum(earnings):,} since {first_year} not including endorsement contracts."
        about_2 = f"He is currently playing for the{current_team}."
    else:
        about_1 = f"{player.split()[0]} earned ${sum(earnings):,} since {first_year} not including endorsement contracts."
        about_2 = f"He retired in {last_year}."

    # Summary line
    print_line(pdf, 11, 0.001, about_1, 8, '')
    # Current status line
    print_line(pdf, 3, 0.001, about_2, 8, '')

    # Career statistics statement
    print_line(pdf, 7, 0.01, 'Career statistics:', 8, '')
    pdf.ln(5)

    # Points per game
    print_stats_graph(years, points, pdf, 'Points per game')
    # Assists per game
    print_stats_graph(years, assists, pdf, 'Assists per game')
    # Rebounds per game
    print_stats_graph(years, rebounds, pdf, 'Rebounds per game')

    # Earnings per year statement
    print_line(pdf, 7, 0.01, 'Earnings per year:', 8, '')
    pdf.ln(5)

    # Earnings graph
    fig, ax = plt.subplots(figsize=(11, 2))
    plt.plot(years, earnings, color=earnings_graph_color, linewidth=1.5)
    set_graph_parameters(ax, '')
    ax = plt.gca()
    mkfunc = lambda x, pos: '%1.1fM' % (x * 1e-6) if x >= 1e6 else '%1.1fK' % (x * 1e-3) if x >= 1e3 else '%1.1f' % x
    mkformatter = FuncFormatter(mkfunc)
    ax.yaxis.set_major_formatter(mkformatter)
    fig.savefig('tmpg.png')
    pdf.image('tmpg.png', x=5, h=20)
    os.remove('tmpg.png')

    # Save file
    pdf.output(f"NBA_{player.replace(' ', '_')}.pdf")
