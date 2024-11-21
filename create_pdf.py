import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import matplotlib.pyplot as plt
import os


def get_info(player):
    filename = f"out_data/{player.replace(' ', '_')}.txt"
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

def create_pdf(player):

    class PDF(FPDF):
        """ Creating the footer for the brochure. """
        def footer(self):
            self.set_y(-15.5)
            self.set_x(-90)
            self.set_font('Helvetica', 'I', 5)
            self.set_text_color(200, 200, 200)
            self.cell(0, 10, text="Data courtesy of Spotrac.com. Team logo downloaded from ESPN.com. Created by apnoorex")
            self.cell(10)
            self.image('in_data/qrcode/qr_code.png', x=113, y=203.8, h=5)

    ### Import data ###
    player_info = get_info(player)
    current_team = player_info[0].split(',')[0].split(':')[-1]

    filename = f"out_data/{player.replace(' ', '_')}.csv"
    stats = pd.read_csv(filename)

    ### Parameters of the brochure ###
    text_color = (105,105,105)
    graph_text_color = '#808080'
    stats_graph_color = '#658585'
    earnings_graph_color = '#677e84'
    linewidth = 1.4

    ### Variables ###
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
    pdf.set_font('helvetica', 'B', size=16)
    pdf.set_text_color(text_color)
    pdf.ln(6)
    pdf.cell(52)
    pdf.cell(text=player.split()[0], new_y=YPos.NEXT)

    # Last name
    pdf.set_font('helvetica', 'B', size=22)
    pdf.ln(2)
    pdf.cell(52)
    pdf.cell(text=player.split()[1], new_y=YPos.NEXT)

    # Position
    pdf.set_font('helvetica', size=8)
    pdf.ln(6)
    pdf.cell(52)
    pdf.cell(text='Position:' + str(player_info[0].split(',')[-1]), new_y=YPos.NEXT)

    # Country
    pdf.ln(1.5)
    pdf.cell(52)
    pdf.cell(text=player_info[2], new_y=YPos.NEXT)

    # Experience
    pdf.ln(1.5)
    pdf.cell(52)
    pdf.cell(text=player_info[1], new_y=YPos.NEXT)

    # Draft info
    pdf.ln(1.5)
    pdf.cell(52)
    pdf.cell(text=player_info[3], new_y=YPos.NEXT)

    # Information block is different for retired and active players
    if player_info[-1] == 'True':
        about_1 = f"{player.split()[0]} has earned ${sum(earnings):,} since {first_year} not including endorsement contracts."
        about_2 = f"He is currently playing for the{current_team}."
    else:
        about_1 = f"{player.split()[0]} earned ${sum(earnings):,} since {first_year} not including endorsement contracts."
        about_2 = f"He retired in {last_year}."

    pdf.set_font('helvetica', size=8)
    pdf.ln(11)
    pdf.cell(text=about_1, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.cell(text=about_2, new_y=YPos.NEXT)
    pdf.ln(7)
    pdf.cell(text='Career statistics:', new_y=YPos.NEXT)
    pdf.ln(5)

    # Points per game
    fig, ax = plt.subplots(figsize=(11, 2))
    plt.plot(years, points, color=stats_graph_color, linewidth=linewidth)
    ax.spines['bottom'].set_color(graph_text_color)
    ax.spines['top'].set_color('#ffffff') 
    ax.spines['right'].set_color('#ffffff')
    ax.spines['left'].set_color(graph_text_color)
    ax.tick_params(axis='x', colors=graph_text_color)
    ax.tick_params(axis='y', colors=graph_text_color)
    plt.title('Points per game', x=0.9, y=0.9, fontsize=8, font='Noto Sans', color='#808080')
    fig.savefig('graph1.png')
    pdf.image('graph1.png', x=5, h=20)

    # Assists per game
    fig, ax = plt.subplots(figsize=(11, 2))
    plt.plot(years, assists, color=stats_graph_color, linewidth=linewidth)
    ax.spines['bottom'].set_color(graph_text_color)
    ax.spines['top'].set_color('#ffffff') 
    ax.spines['right'].set_color('#ffffff')
    ax.spines['left'].set_color(graph_text_color)
    ax.tick_params(axis='x', colors=graph_text_color)
    ax.tick_params(axis='y', colors=graph_text_color)
    plt.title('Assists per game', x=0.9, y=0.9, fontsize=8, font='Noto Sans', color='#808080')
    fig.savefig('graph2.png')
    pdf.image('graph2.png', x=5, h=20)

    # Rebounds per game
    fig, ax = plt.subplots(figsize=(11, 2))
    plt.plot(years, rebounds, color=stats_graph_color, linewidth=linewidth)
    ax.spines['bottom'].set_color(graph_text_color)
    ax.spines['top'].set_color('#ffffff') 
    ax.spines['right'].set_color('#ffffff')
    ax.spines['left'].set_color(graph_text_color)
    ax.tick_params(axis='x', colors=graph_text_color)
    ax.tick_params(axis='y', colors=graph_text_color)
    plt.title('Rebounds per game', x=0.9, y=0.9, fontsize=8, font='Noto Sans', color='#808080')
    fig.savefig('graph3.png')
    pdf.image('graph3.png', x=5, h=20)

    # Earnings per year
    pdf.set_font('helvetica', size=8)
    pdf.set_text_color(text_color)
    pdf.ln(7)
    pdf.cell(text='Earnings per year:', new_y=YPos.NEXT)
    pdf.ln(5)
    fig, ax = plt.subplots(figsize=(11, 2))
    plt.plot(years, earnings, color=earnings_graph_color, linewidth=1.5)
    ax.spines['bottom'].set_color(graph_text_color)
    ax.spines['top'].set_color('#ffffff') 
    ax.spines['right'].set_color('#ffffff')
    ax.spines['left'].set_color(graph_text_color)
    ax.tick_params(axis='x', colors=graph_text_color)
    ax.tick_params(axis='y', colors=graph_text_color)
    # plt.ticklabel_format(axis="y", style='plain')   
    plt.title('', x=0.9, y=0.9, fontsize=8, font='Noto Sans', color='#808080')
    fig.savefig('graph4.png')
    pdf.image('graph4.png', x=5, h=20)

    # Save file
    pdf.output(f"NBA_{player.replace(' ', '_')}.pdf")

    # Remove tmp files.
    os.remove('graph1.png')
    os.remove('graph2.png')
    os.remove('graph3.png')
    os.remove('graph4.png')
