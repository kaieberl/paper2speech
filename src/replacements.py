text_replacements = [
    ("i\.e\.", 'that is'),
    ("e\.g\.", 'for example'),
    ("e\. g\.", 'for example'),
    ("i\.i\.d\.", 'i i d'),
    ("Eq\.", 'Equation'),
    ("eq\.", 'equation'),
    ("Fig\.", 'Figure'),
    ("fig\.", 'figure'),
    ("Sec\.", 'Section'),
    ("sec\.", 'section'),
    ("Tab\.", 'Table'),
    ("tab\.", 'table'),
    ("Thm\.", 'Theorem'),
    ("thm\.", 'theorem'),
    ("vs\.", 'versus'),
    ("w\.r\.t\.", 'with respect to'),
    ("w\.r\.t", 'with respect to'),
    ("w\.l\.o\.g\.", 'without loss of generality'),
    (r"\((.*?)\)-th", r"\1-th"),
    # remove numbers after sentences, e.g. ... of training.4
    (r'(\w+)\.(\d+)$', r'\1'),
    # add break after title number
    (r'#+\s+(\d+(\.\d+)*)\s+', r'<s>\1</s>'),
    (r' et al.', ' et al'),
    # remove ssml closing tags
    (r'<break time="0.5s"></break>', r'<break time="0.5s"/>'),
    # remove references
    (r'\s*(\[[0-9,-, ]+(, pp\. [0-9,-]+|, p\.\d+[f]?[f]?\.?)?\]|\([0-9,-, ]+(, pp\. [0-9,-]+|, p\.\d+[f]?[f]?\.?)?\))', ''),
    (r'\s*\[[^\]]*, \d{4}(?:, [^\]]*, \d{4})*\]', ''),
    (r'\s*\([^\)]*, \d{4}(?:[;,] [^\)]*, \d{4}[a-zA-Z]*?)*\)', ''),
    (r'\s*(\b\w+\s+et al\.) (\[\d{4}\]|\(\d{4}\))', r'\1'),
    # remove urls
    (r'\s*https?://[\w/:%#\$&\?\(\)~\.=\+\-]*[\w\d_\-]', ''),
    # remove new lines
    (r'\n', ''),
]

math_replacements = [
    # combined symbols
    (r'\\lVert\\cdot\\rVert', 'norm'),

    # Basic arithmetic operations
    (r'\+', 'plus'),
    (r'-', 'minus'),
    (r'\*', 'times'),
    (r'/', 'divided by'),
    (r'\^\{\\circ\}', 'degrees'),

    # Fractions and powers
    (r'\^2', 'squared'),
    (r'\^3', 'cubed'),
    (r'\^\{T\}', 'transpose'),
    (r'\\frac{([^}]+)}{([^}]+)}', r'\1 over \2'),

    # Roots
    (r'\\sqrt{([^}]+)}', 'square root of \1'),
    (r'\\sqrt\[3]{([^}]+)}', 'cube root of \1'),
    (r'\\sqrt\[(\d+)]{([^}]+)}', r'\1-th root of \2'),

    # Calculus symbols
    (r'\\int', 'integral'),
    (r'\\sum', 'summation over'),
    (r'\\lim', 'limit'),
    (r'\\infty', 'infinity'),

    # Basic mathematical symbols
    (r'\\pm', 'plus or minus'),
    (r'\\times', 'times'),
    (r'\\div', 'divided by'),
    (r'\\cdot', 'times'),
    (r'\\leq', 'less than or equal to'),
    (r'\\geq', 'greater than or equal to'),
    (r'>', 'greater'),
    (r'<', 'less than'),
    (r'\\neq', 'not equal to'),
    (r'\\approx', 'approximately'),
    (r'\\equiv', 'equivalent to'),

    # Quantifiers and logic symbols
    (r'\\forall', 'for all'),
    (r'\\exists', 'there exists'),
    (r'\\rightarrow', 'goes to'),
    (r'\\Rightarrow', 'implies'),
    (r'\\mapsto', 'maps to'),
    (r'\\in', 'in'),

    # Greek letters
    (r'\\alpha', 'alpha'),
    (r'\\beta', 'beta'),
    (r'\\gamma', 'gamma'),
    (r'\\delta', 'delta'),
    (r'\\epsilon', 'epsilon'),
    (r'\\zeta', 'zeta'),
    (r'\\eta', 'eta'),
    (r'\\theta', 'theta'),
    (r'\\iota', 'iota'),
    (r'\\kappa', 'kappa'),
    (r'\\lambda', 'lambda'),
    (r'\\mu', 'mu'),
    (r'\\nu', 'nu'),
    (r'\\xi', 'ksi'),
    (r'\\pi', 'pi'),
    (r'\\rho', 'rho'),
    (r'\\sigma', 'sigma'),
    (r'\\tau', 'tau'),
    (r'\\upsilon', 'upsilon'),
    (r'\\phi', 'phi'),

    # Trigonometric functions
    (r'\\sin', 'sine'),
    (r'\\cos', 'cosine'),
    (r'\\tan', 'tangent'),
    (r'\\cot', 'cotangent'),
    (r'\\arcsin', 'arcsine'),
    (r'\\arccos', 'arccosine'),
    (r'\\arctan', 'arctangent'),

    # Set notation
    (r'\\emptyset', 'empty set'),
    (r'\\subseteq', 'is a subset of or equal to'),
    (r'\\superset', 'superset'),
    (r'\\cup', 'union'),
    (r'\\cap', 'intersection'),
    (r'\\notin', 'is not an element of'),
    (r'\\subset', 'subset'),
    (r'\\setminus', 'set minus'),
    (r'\\operatorname\{supp}', 'support of'),

    # Other symbols
    (r'\\mathbb\{E}', 'expectation'),
    (r'\\hat\{([^}]+)}', r'\1 hat'),
    (r'\\bar\{([^}]+)}', r'\1 bar'),
    (r'\\tilde\{([^}]+)}', r'\1 tilde'),
    (r'\\dot\{([^}]+)}', r'\1 dot'),
    (r'\\ddot\{([^}]+)}', r'\1 double dot'),
    (r'\\mathcal\{([^}]+)}', r'\1'),
    (r'\\mathbb\{([^}]+)}', r'\1'),
    (r'\\mathbf\{([^}]+)}', r'\1'),
    (r'\\mathcal\{([^}]+)}', r'\1'),
    (r'\\lVert', 'norm of'),
    (r'\\rVert', ''),
    (r'\\langle', ''),
    (r'\\rangle', ''),
    (r'\\dots', ''),
    (r'\\ldots', ''),
    (r'\\mid', ''),

    # Removing unnecessary LaTeX commands
    (r'\\big{(.*?)}', r'\1'),
    (r'\\boldsymbol', ''),
    (r'\\left', ''),
    (r'\\right', ''),
    (r'\^', ''),
    (r'\|', ''),
    (r'\\', ''),
    (r'_', ''),
    (r'{', ''),
    (r'}', ''),
]
