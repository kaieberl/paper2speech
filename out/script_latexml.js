// =================== FOR TESTING ===================

// const originalFetch = window.fetch;
//
// window.fetch = function (url, options) {
//   // You can inspect the URL and options to decide how to respond
//   console.log('URL:', url);
//   console.log('Options:', options.body);
//
//   const requestBody = JSON.parse(options.body);
//
//   // Check the model in the request
//   if (requestBody.model && requestBody.model.startsWith('gpt-')) {
//     // Return a promise that resolves with a Response object
//     return Promise.resolve({
//       ok: true, // or false if you want to simulate an error response
//       json: function () {
//         return Promise.resolve({
//           choices: [
//             {
//               message: {
//                 content: 'This is a test $\\mathbb{R}^{\\hat}.',
//               }
//             }
//           ]
//         });
//       }
//     });
//   } else {
//     return originalFetch(url, options);
//   }
// };

// =================== END FOR TESTING ===================

const OPENAI_API_KEY = 'sk-XXX'


function getExplanation(text) {
  // =================== COPY TO CLIPBOARD ===================
  // navigator.clipboard.writeText(text);
  // window.getSelection().removeAllRanges();
  // return;
  // =================== END COPY TO CLIPBOARD ===================

  return fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + OPENAI_API_KEY
    },
    body: JSON.stringify({
      'model': 'gpt-4o',
      'messages': [
        {
          'role': 'system',
          'content': 'Enclose all math expressions in dollar signs ($).'
        },
        {
          'role': 'user',
          'content': text.substring(0, 4096),
        }
      ],
      'max_tokens': 1024
    })
  })
    .then(response => response.json())
    .then(data => data.choices[0].message.content)
    .catch(error => {
      console.error('Error fetching explanation:', error);
    });
}

function getSectionText(section) {
  const sectionCopy = section.cloneNode(true);
  sectionCopy.querySelectorAll('button').forEach(button => button.remove());
  // replace all math elements with their alttext
  sectionCopy.querySelectorAll('math').forEach(math => {
    const altText = math.getAttribute('alttext');
    const altTextSpan = document.createElement('span');
    altTextSpan.textContent = altText;
    math.replaceWith(altTextSpan);
  });
  return sectionCopy.textContent.replace(/\n/g, ' ').replace(/\s+/g, ' ');
}

function explainButton(button) {
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'loading';
  button.appendChild(loadingDiv);
  button.disabled = true; // Disable button

  const prompt = 'Explain this:\n' + getSectionText(button.parentElement);
  getExplanation(prompt).then(explanation => {
    readAloud(explanation, button);
  });
}

// replace LaTeX expressions with their spoken equivalent inside math-inline spans
const mathReplacements = [
  // Basic arithmetic operations
  {find: /\+/g, replace: 'plus'},
  {find: /-/g, replace: 'minus'},
  {find: /\*/g, replace: 'star'},
  {find: /\//g, replace: 'divided by'},
  {find: /\^\{\\circ}/g, replace: 'degrees'},

  // Fractions and powers
  {find: /\\frac{([^}]+)}{([^}]+)}/g, replace: '$1 over $2'},
  {find: /\^2/g, replace: 'squared'},
  {find: /\^3/g, replace: 'cubed'},

  // Roots
  {find: /\\sqrt{([^}]+)}/g, replace: 'square root of $1'},
  {find: /\\sqrt\[3]{([^}]+)}/g, replace: 'cube root of $1'},
  {find: /\\sqrt\[(\d+)]{([^}]+)}/g, replace: '$1-th root of $2'},

  // Calculus symbols
  {find: /\\int/g, replace: 'integral'},
  {find: /\\sum/g, replace: 'summation'},
  {find: /\\lim/g, replace: 'limit'},
  {find: /\\infty/g, replace: 'infinity'},

  // Basic mathematical symbols
  {find: /\\pm/g, replace: 'plus or minus'},
  {find: /\\times/g, replace: 'times'},
  {find: /\\div/g, replace: 'divided by'},
  {find: /\\cdot/g, replace: 'times'},
  {find: /\\leq/g, replace: 'less than or equal to'},
  {find: /\\geq/g, replace: 'greater than or equal to'},
  {find: />/g, replace: 'greater'},
  {find: /</g, replace: 'less than'},
  {find: /\\neq/g, replace: 'not equal to'},
  {find: /\\approx/g, replace: 'approximately'},
  {find: /\\equiv/g, replace: 'equivalent to'},

  // Quantifiers and logic symbols
  {find: /\\forall/g, replace: 'for all'},
  {find: /\\exists/g, replace: 'there exists'},
  {find: /\\rightarrow/g, replace: 'goes to'},
  {find: /\\Rightarrow/g, replace: 'implies'},
  {find: /\\mapsto/g, replace: 'maps to'},
  {find: /\\in/g, replace: 'in'},

  // Greek letters
  {find: /\\alpha/g, replace: 'alpha'},
  {find: /\\beta/g, replace: 'beta'},
  {find: /\\gamma/g, replace: 'gamma'},
  {find: /\\delta/g, replace: 'delta'},
  {find: /\\epsilon/g, replace: 'epsilon'},
  {find: /\\zeta/g, replace: 'zeta'},
  {find: /\\eta/g, replace: 'eta'},
  {find: /\\theta/g, replace: 'theta'},
  {find: /\\iota/g, replace: 'iota'},
  {find: /\\kappa/g, replace: 'kappa'},
  {find: /\\lambda/g, replace: 'lambda'},
  {find: /\\mu/g, replace: 'mu'},
  {find: /\\nu/g, replace: 'nu'},
  {find: /\\xi/g, replace: 'ksi'},
  {find: /\\pi/g, replace: 'pi'},
  {find: /\\rho/g, replace: 'rho'},
  {find: /\\sigma/g, replace: 'sigma'},
  {find: /\\tau/g, replace: 'tau'},
  {find: /\\upsilon/g, replace: 'upsilon'},
  {find: /\\phi/g, replace: 'phi'},

  // Trigonometric functions
  {find: /\\sin/g, replace: 'sine'},
  {find: /\\cos/g, replace: 'cosine'},
  {find: /\\tan/g, replace: 'tangent'},
  {find: /\\cot/g, replace: 'cotangent'},
  {find: /\\arcsin/g, replace: 'arcsine'},
  {find: /\\arccos/g, replace: 'arccosine'},
  {find: /\\arctan/g, replace: 'arctangent'},

  // Set notation
  {find: /\\emptyset/g, replace: 'empty set'},
  {find: /\\subseteq/g, replace: 'is a subset of or equal to'},
  {find: /\\superset/g, replace: 'superset'},
  {find: /\\cup/g, replace: 'union'},
  {find: /\\cap/g, replace: 'intersection'},
  {find: /\\notin/g, replace: 'is not an element of'},
  {find: /\\subset/g, replace: 'subset'},
  {find: /\\setminus/g, replace: 'without'},
  {find: /\\operatorname\{supp}/g, replace: 'support of'},

  // Other symbols
  {find: /\\langle/g, replace: ''},
  {find: /\\rangle/g, replace: ''},
  {find: /\\mathbb\{E}/g, replace: 'expectation'},
  {find: /\\hat\{([^}]+)}/g, replace: '$1 hat'},
  {find: /\\bar\{([^}]+)}/g, replace: '$1 bar'},
  {find: /\\tilde\{([^}]+)}/g, replace: '$1 tilde'},
  {find: /\\dot\{([^}]+)}/g, replace: '$1 dot'},
  {find: /\\ddot\{([^}]+)}/g, replace: '$1 double dot'},
  {find: /\\mathcal\{([^}]+)}/g, replace: '$1'},
  {find: /\\mathbb\{([^}]+)}/g, replace: '$1'},
  {find: /\\mathbf\{([^}]+)}/g, replace: '$1'},
  {find: /\\mathcal\{([^}]+)}/g, replace: '$1'},
  {find: /\\lVert/g, replace: 'norm of'},
  {find: /\\rVert/g, replace: ''},
  {find: /\\langle/g, replace: ''},
  {find: /\\rangle/g, replace: ''},
  {find: /\\dots/g, replace: ''},
  {find: /\\ldots/g, replace: ''},
  {find: /\\mid/g, replace: ''},

  // Removing unnecessary LaTeX commands
  {find: /\\big{(.*?)}/g, replace: '$1'},
  {find: /\\left/g, replace: ''},
  {find: /\\right/g, replace: ''},
  {find: /\^/g, replace: ''},
  {find: /\|/g, replace: ''},
  {find: /\\/g, replace: ''},
  {find: /\{/g, replace: ''},
  {find: /}/g, replace: ''},
  {find: /_/g, replace: ''},
  {find: / {3}/g, replace: ''},
];

const textReplacements = [
  {find: /w\.r\.t\./g, replace: 'with respect to'},
  {find: /a\.e\./g, replace: 'almost everywhere'},
  {find: /a\.s\./g, replace: 'almost surely'},
  {find: /s\.t\./g, replace: 'such that'},
  {find: /i\.i\.d\./g, replace: 'independent and identically distributed'},
  {find: /i\.e\./g, replace: 'that is'},
  {find: /e\.g\./g, replace: 'for example'},
  {find: /cf\./g, replace: 'compare'},
  {find: /sec\./g, replace: 'section'},
  {find: /Sec\./g, replace: 'section'},
  {find: /thm\./g, replace: 'theorem'},
  {find: /Thm\./g, replace: 'theorem'},
  {find: /ex\./g, replace: 'example'},
  {find: /Ex\./g, replace: 'example'},
  {find: /eq\./g, replace: 'equation'},
  {find: /Eq\./g, replace: 'equation'},
  {find: /def\./g, replace: 'definition'},
  {find: /Def\./g, replace: 'definition'},
];

function handleExplainButton(buttonElement) {
  if (buttonElement.querySelector('span').textContent === 'pause') {
    buttonElement.querySelector('span').textContent = 'play_arrow';
    buttonElement.nextElementSibling.pause();
  } else if (buttonElement.querySelector('span').textContent === 'play_arrow') {
    buttonElement.querySelector('span').textContent = 'pause';
    // rewind 1 second if the audio is not at the end
    if (buttonElement.nextElementSibling.currentTime < buttonElement.nextElementSibling.duration) {
      buttonElement.nextElementSibling.currentTime -= 1;
    }
    buttonElement.nextElementSibling.play();
  } else {
    explainButton(buttonElement)
  }
}

function readAloud(text, buttonElement) {
  const options = {
    htmlTags: true,
    outMath: {
      include_latex: true,
    },
  };
  var explanation = document.createElement('div');
  explanation.innerHTML = markdownToHTML(text, options);

  var allTextContents = '';
  var mathblocks = explanation.getElementsByClassName('math-block');
  for (var i = 0; i < mathblocks.length; i++) {
    mathblocks[i].textContent = '.';
  }
  var mathinlines = explanation.getElementsByClassName('math-inline');
  for (var i = 0; i < mathinlines.length; i++) {
    var mathinline = mathinlines[i];
    for (var j = 0; j < mathReplacements.length; j++) {
      mathinline.textContent = mathinline.textContent.replace(mathReplacements[j].find, ' ' + mathReplacements[j].replace + ' ');
    }
  }
  // remove newlines within divs and add a newline at the end
  allTextContents += explanation.textContent.replace(/\n/g, '') + '\n';

  for (var i = 0; i < textReplacements.length; i++) {
    allTextContents = allTextContents.replace(textReplacements[i].find, textReplacements[i].replace);
  }
  console.log(allTextContents);

  fetch('https://api.openai.com/v1/audio/speech', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + OPENAI_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      'model': 'tts-1',
      'input': allTextContents.substring(0, 4096),
      'voice': 'echo'
    })
  })
    .then(response => response.blob())
    .then(blob => {
      buttonElement.disabled = false; // Re-enable button
      var audio = document.createElement('audio');
      audio.src = URL.createObjectURL(blob);

      buttonElement.parentElement.insertBefore(audio, buttonElement.nextElementSibling);
      // change button icon to pause
      buttonElement.querySelector('span').textContent = 'pause';
      buttonElement.querySelector('div').remove();

      audio.play()
        .then(() => {
          audio.onended = function () {
            buttonElement.querySelector('span').textContent = 'play_arrow';
          }
        });
    });
}

function handleChatButton(button) {
  const selection = window.getSelection();
  button.remove();
  if (!selection.isCollapsed) {
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    button.style.left = `${(rect.left + rect.right) / 2 - 29}px`;
    button.style.top = `${rect.top - button.offsetHeight - 16}px`;
    document.body.appendChild(button);
  }
}

document.addEventListener("DOMContentLoaded", function(event) {
  let button = document.createElement('button');
  const chatSpan = document.createElement('span');
  chatSpan.className = 'material-icons-round';
  chatSpan.textContent = 'chat_bubble';
  button.appendChild(chatSpan);
  button.className = 'start-chat-button';
  button.onclick = function () {
    chatButton(button);
  }

  document.body.addEventListener('click', function (event) {
    handleChatButton(button);
  });
});

const headings = document.querySelectorAll('h2, h3, h4, h6');
headings.forEach(heading => {
  const newButton = document.createElement('button');
  newButton.onclick = function () {
    handleExplainButton(newButton);
  };
  newButton.className = 'explain-section-button';
  const explainSpan = document.createElement('span');
  explainSpan.className = 'material-icons-round';
  explainSpan.textContent = 'auto_awesome';
  newButton.appendChild(explainSpan);

  // Insert the button after the heading
  heading.parentNode.insertBefore(newButton, heading.nextSibling);
});
