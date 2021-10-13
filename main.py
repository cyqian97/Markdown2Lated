import sys
import re
import warnings
import argparse


def markdown2latex(lines_md, _level_shift, _level_unnumbered):
    # When writing md files:
    #   1. Do not use \matrix, use \begin{matrix} and \end{matrix} instead
    #   2. Always start a new line for \label{}\tag{}
    lines_tex = []
    levels_tex = ("part", "chapter", "section", "subsection", "subsubsection", "paragraph", "subparagraph")
    levels_md = ("# ", "## ", "### ", "#### ", "##### ", "###### ")

    # math
    flag_mathblock = False
    flag_findbegin = False
    flag_needeq = False
    label = ""

    for l in lines_md:
        l_temp = l
        if re.match('\$\$', l_temp):
            flag_mathblock = not flag_mathblock
            if not flag_mathblock:
                if flag_needeq:
                    lines_tex.append("\\end{split}\n" + label + "\\end{equation*}\n")
                    label = ""
                flag_findbegin = False
                flag_needeq = False
            continue
        if flag_mathblock:
            if flag_findbegin:
                if re.match(r'\s*\\newcommand', l_temp):
                    continue
                if re.match(r'\s*\\end\{align\}', l_temp):
                    continue
                if re.match(r'\s*\\label\{', l_temp):
                    label = l_temp
                    continue

                lines_tex.append(l_temp)
            elif re.match(r'\s*\\newcommand', l_temp):
                flag_findbegin = True
                continue
            elif re.match(r'\s*\\begin\{align\}', l_temp):
                lines_tex.append("\\begin{equation*}\n\\begin{split}\n")
                flag_findbegin = True
                flag_needeq = True
            else:
                lines_tex.append("\\begin{equation*}\n\\begin{split}\n")
                flag_findbegin = True
                flag_needeq = True
                lines_tex.append(l_temp)
            continue

        # titles
        for i in range(min(levels_tex.__len__() - _level_shift, levels_md.__len__())):
            title_md = levels_md[i]
            if re.match(title_md, l_temp):
                if i >= _level_unnumbered:
                    l_temp = "\\" + levels_tex[i + _level_shift] + "*{" + l_temp.split('# ')[1][:-1] + "}\n"
                else:
                    l_temp = "\\" + levels_tex[i + _level_shift] + "{" + l_temp.split('# ')[1][:-1] + "}\n"

        # boldface
        result = re.search('\*\*.*\*\*', l_temp)
        while result:
            l_temp = l_temp[:result.span()[0]] + r"\textbf{" + l_temp[result.span()[0] + 2:result.span()[1] - 2] + "}" \
                     + l_temp[result.span()[1]:]
            result = re.search('\*\*.*\*\*', l_temp)

        # italic
        result = re.search('\*.*\*', l_temp)
        while result:
            l_temp = l_temp[:result.span()[0]] + r"\textit{" + l_temp[result.span()[0] + 1:result.span()[1] - 1] + "}" \
                     + l_temp[result.span()[1]:]
            result = re.search('\*.*\*', l_temp)

        result = re.findall(r'<img\s*src="([^"]+)"', l_temp)
        if result:
            lines_tex += ["\\begin{figure}[htbp]\n",
                          "\t\\centering\n",
                          "\t\\includegraphics[trim=0 0 0 0,clip=true,scale=.5]{img/" + result[0] + "}\n",
                          "\t\\caption{}\n",
                          "\t\\label{fig:" + result[0].rsplit('.', 1)[0] + "}\n",
                          "\\end{figure})\n"]
            l_temp = "\n"
        lines_tex.append(l_temp)

    return lines_tex


filein = r"C:\Users\selen\OneDrive - Texas A&M University\Project\Linear-time Encodable Codes\Notes\Note on Sipser1996.md"
fileout = r"C:\Users\selen\OneDrive - Texas A&M University\Project\Linear-time Encodable Codes\Notes\Note on Sipser1996.tex"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filein', type=str, default=filein, help="Full path to the input markdown file.")
    parser.add_argument('--fileout', type=str, default=fileout, help="Full path to the output latex file.")
    parser.add_argument('--lshift', type=int, default=2, help="Latex title level minus markdown title level.")
    parser.add_argument('--lunnum', type=int, default=3, help="Titles will correspond to unnumbered with markdown "
                                                              "levels no less than this value.")
    p = parser.parse_args()

    if not p.fileout:
        p.fileout = p.filein.rsplit('.', 1)[0] + ".tex"

    with open(p.filein, 'r', encoding="utf-8") as fid:
        lines = fid.readlines()

    fid = open(p.fileout, 'w', encoding="utf-8")
    fid.writelines(markdown2latex(lines, p.lshift, p.lunnum))
