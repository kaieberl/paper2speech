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

function handleExplainButton(button) {
  const prompt = 'Explain this:\n' + getSectionText(button.parentElement);
  // copy to clipboard
  navigator.clipboard.writeText(prompt);
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

document.addEventListener("DOMContentLoaded", function (event) {
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
