import os
import pylatex as pex

ASSIGNMENT = "Assignment 1"
GENERIC_TEXT = """
\section*{Rubric}
\subsection*{Question 1}
\begin{itemize}
\item 10 pts for correct LP model
\item 10 pts for correct implementation
\item 10 pts for correct plot
\end{itemize}
"""

doc = pex.Document(geometry_options={"tmargin": "3cm", "lmargin": "1.5cm", "rmargin": "1.5cm", "bmargin": "2cm"})
doc.packages.append(pex.Package('amsmath'))
doc.packages.append(pex.Package('babel',options='english')) 

def create_pdf(student, grade, breakdown, path=""):
	doc = pex.Document(geometry_options={"tmargin": "3cm", "lmargin": "1.5cm", "rmargin": "1.5cm", "bmargin": "2cm"})
	doc.packages.append(pex.Package('amsmath'))
	doc.packages.append(pex.Package('titling')) 
	doc.packages.append(pex.Package('xcolor'))
	doc.packages.append(pex.Package('babel',options='english')) 

	doc.preamble.append(pex.NoEscape(r'\setlength{\droptitle}{-3cm}'))
	doc.preamble.append(pex.NoEscape(r'\inputencoding{utf8}')) 
	doc.preamble.append(pex.NoEscape(r'\thispagestyle{empty}')) 
	doc.preamble.append(pex.NoEscape(r'\setlength\parindent{0pt}'))
	doc.preamble.append(pex.NoEscape(r'\AtBeginDocument{\selectlanguage{english}}'))

	doc.preamble.append(pex.Command('title', f'Feedback on {ASSIGNMENT} by {student.firstname} {(student.middlename + " " + student.lastname).strip()}'))
	doc.preamble.append(pex.Command('author', pex.NoEscape(r'Jasper van Doorn, Leon Lan, Rosario Paradiso \& Alessandro Zocca')))
	doc.preamble.append(pex.Command('date', pex.NoEscape(r'\today')))
	doc.append(pex.NoEscape(r'\maketitle'))    

	doc.append(pex.NoEscape(r'The grade of your %s is \textbf{%.2f / 100}. Below find the detailed feedback below.' % (ASSIGNMENT, grade + 0.0001)))

	doc.append(pex.NoEscape(GENERIC_TEXT))

	for k, v in breakdown:
		with doc.create(pex.Section(f"{k}: {v['points']:g}',numbering=False)):
			doc.append(pex.NoEscape(v.get("feedback", "")))

	filename = os.path.join(path, f"{student.vunet_id}-feedback"
	doc.generate_pdf(filename, clean=True, clean_tex=True, silent=True, compiler="pdflatex")

	return filename
