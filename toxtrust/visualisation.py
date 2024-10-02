
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os

def beliefPlausibility(name, item, threshold, path):
    
    try:
    
        data = {'Negative': item['belief']['negative'] + (item['plausibility']['negative'] - item['belief']['negative'])/2,'Positive': item['belief']['positive'] + (item['plausibility']['positive'] - item['belief']['positive'])/2}

        y_error = item['probabilities']['uncertain']/2 # assuming equal ledatael of ignorance for each prediction from a constant source
        
        x, y = [], []

        for key, value in data.items():

            if value != 0:

                x.append(key)
                y.append(value)

        plt.figure(figsize=(3.5,2.75))
        plt.errorbar(x, y, yerr = y_error,linestyle="", capsize=6,elinewidth=2,markeredgewidth=2, color='black')

        #plt.xlabel('Outcome', fontsize=15, labelpad=17)
        plt.ylabel('Probability', fontsize=13, labelpad=10)

        plt.xticks(fontsize=13)
        plt.yticks(np.arange(0, 1.05, step=0.1), fontsize=9)
        plt.ylim(bottom = -0.15,top=1.15)
        plt.margins(0.45)

        plt.title(f'Probability intervals for "{name}"', fontsize=13, pad=8)

        font = {'color':  'black',
                'weight': 'normal',
                'size': 14,
                'style':'italic'
                }

        if len(x) == 2:

            plt.text(x=-0.13,y= (data['Negative'] - y_error - 0.09), s='Belief', fontdict=font, size=10)
            plt.text(x=-0.2,y= (data['Negative'] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

            plt.text(x=0.88,y= (data['Positive'] - y_error - 0.09), s='Belief', fontdict=font, size=10)
            plt.text(x=0.79,y= (data['Positive'] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

        else:

            plt.text(x = -0.014,y= (data[x[0]] - y_error - 0.10), s='Belief', fontdict=font, size=10)
            plt.text(x = -0.023,y= (data[x[0]] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

        plt.axhline(y = threshold, color = 'r', linestyle = 'dashed')  
        
        savePath = os.path.join(path, name + '.png')

        plt.savefig(savePath)
        
        return True, 'Image generation successful'
    
    except:
        
        return False, 'Image generation failed'
    
def visualiseCombination(labels, data, path):

    # chosen = self.ReturnResults(selection)
    
    # labels = [item + str("'s rule") if item in ['Dempster','Yager','Inagaki'] else item for item in chosen.index ] #["Combination result" if item in ['Dempster','Yager','Inagaki'] else item for item in chosen.index ]
    
    # data = np.array(chosen)    

    try:
        data_cum = data.cumsum(axis=1)
        category_names = ['Negative', 'Uncertain', 'Positive']

        category_colors = matplotlib.cm.get_cmap('Blues')(np.linspace(0.15,0.75, data.shape[1]))

        # if len (chosen.index) == 1:
        #     fig, ax = plt.subplots(figsize=(8.5, 1.1))

        # else:

        bar_height = 1.1 * (1 + len(labels))
        fig, ax = plt.subplots(figsize=(8.5, bar_height))

        ax.invert_yaxis()
        ax.xaxis.set_visible(False)

        ax.set_xlim(0, np.sum(data, axis=1).max())
        ax.yaxis.set_ticks_position('none')

        text_color = 'black'
        for i, (colname, color) in enumerate(zip(category_names, category_colors)):
            widths = data[:, i]
            starts = data_cum[:, i] - widths
            ax.barh(labels, widths, left=starts, height=0.8,
                    label=colname, color=color)
            plt.yticks(fontsize=14, fontname='Arial',style='italic') #### changes
            xcenters = starts + widths / 2

            r, g, b, _ = color
            for y, (x, c) in enumerate(zip(xcenters, widths)):

                if c != 0.0:
                    ax.text(x, y, str(round(c,2)), ha='center', va='center',
                        color=text_color, fontsize=12,fontname= "Arial") #fontweight="bold"

        ax.legend(ncol=len(category_names), bbox_to_anchor=(-0.015, -0.14),
                    loc='lower left', fontsize=12)

        # if selection is None:
        #     ax.axhline(len(self.ReturnResults('bpa'))-0.5, color ='black', linewidth=0.8, linestyle='--') 


        plt.title(f'Evidence combination for {labels[-1]})', fontsize=15, pad=13)

        savePath = os.path.join(path, 'combination.png')

        plt.savefig(savePath)

        return True, 'Image generation successful'

    except:
            
        return False, 'Image generation failed'