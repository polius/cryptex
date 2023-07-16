// Apply autosize in all textarea components
autosize(document.querySelectorAll('textarea'));

// Get the search parameters from the current URL
const urlParams = new URLSearchParams(window.location.search);

// Store previous step (for about)
var previousStep = null

// Get all components
const about = document.getElementById('about');
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const step4 = document.getElementById('step4');
const step5 = document.getElementById('step5');

const theme_text = document.getElementById('theme-text');
const about_text = document.getElementById('about-text');

const step1_message = document.getElementById('step1-message');
const step1_message_count = document.getElementById('step1-message-count');
const step1_error = document.getElementById('step1-error');
const step1_password = document.getElementById('step1-password');
const step1_password_count = document.getElementById('step1-password-count');
const step1_button = document.getElementById('step1-button');
const step1_button_icon = document.getElementById('step1-button-icon');
const step1_button_loading = document.getElementById('step1-button-loading');

const step2_url = document.getElementById('step2-url')
const step2_copy_url = document.getElementById('step2-copy-url')

const step3_password = document.getElementById('step3-password');
const step3_password_count = document.getElementById('step3-password-count');
const step3_button = document.getElementById('step3-button');
const step3_button_icon = document.getElementById('step3-button-icon');
const step3_button_loading = document.getElementById('step3-button-loading');
const step3_error = document.getElementById('step3-error');

const step4_message = document.getElementById('step4-message');
const step4_expiration = document.getElementById('step4-expiration');
const step4_button_copy = document.getElementById('step4-button-copy');
const step4_copy_message = document.getElementById('step4-copy-message');
const step4_button_delete = document.getElementById('step4-button-delete');
const step4_button_delete_confirm = document.getElementById('step4-button-delete-confirm');
const step4_message_error = document.getElementById('step4-message-error');
const step4_button_icon = document.getElementById('step4-button-icon');
const step4_button_loading = document.getElementById('step4-button-loading');

const footer = document.getElementById('footer');

// Get theme mode
const mode = window.localStorage.getItem('mode')
if (mode == 'dark') theme_text.innerHTML = 'Dark'

// Execute on page load
window.addEventListener("load", () => {
  // Clean inputs and textareas
  step1_message.value = urlParams.get('m') == null ? '' : urlParams.get('m')
  step1_password.value = ''
  step3_password.value = ''

  // Add fade-in effect and focus the current input
  const element = window.location.pathname != '/' ? step3 : step1
  const element_focus = window.location.pathname != '/' ? step3_password : step1_message
  let opacity = 0;
  element.style.display = 'block';
  element.style.opacity = opacity;
  let intervalID = setInterval(() => {
    if (opacity < 1) {
      opacity = opacity + 0.1
      element.style.opacity = opacity;
    } else {
      clearInterval(intervalID);
      element_focus.focus()
    }
  }, 20);
  footer.style.display = 'block'
});

// Theme
function themeClick() {
  if (theme_text.innerHTML == 'Dark') {
    theme_text.innerHTML = 'Light'
    document.documentElement.classList.remove("dark")
    document.documentElement.classList.add("light")
    window.localStorage.setItem('mode', 'light')
  }
  else if (theme_text.innerHTML == 'Light') {
    theme_text.innerHTML = 'Dark'
    document.documentElement.classList.remove("light")
    document.documentElement.classList.add("dark")
    window.localStorage.setItem('mode', 'dark')
  }
}

// About
function aboutClick() {
  if (about_text.innerHTML == 'About') {
    const currentStep = [step1, step2, step3, step4, step5].find(x => x.style.display != 'none')
    previousStep = currentStep
    currentStep.style.display = 'none'
    about.style.display = 'block'
    about_text.innerHTML = 'Go back'
  }
  else {
    about.style.display = 'none'
    about_text.innerHTML = 'About'
    previousStep.style.display = 'block'
  }
}

// Step 1
step1_message.addEventListener('input', () => {
  step1_message_count.textContent = `${step1_message.value.length} / 1000`
  if (step1_message.value.length > 1000) step1_message_count.style.color = '#dc3545'
  else step1_message_count.style.color = theme_text.innerHTML == 'Dark' ? '#adb5db' : '#212529'
});

step1_password.addEventListener('input', () => {
  step1_password_count.textContent = `${step1_password.value.length} / 100`
  if (step1_password.value.length > 100) step1_password_count.style.color = '#dc3545'
  else step1_password_count.style.color = theme_text.innerHTML == 'Dark' ? '#adb5db' : '#212529'
});

step1_password.addEventListener("keydown", (e) => {
  if (e.code === "Enter") step1_button_click()
});

function togglePassword1Visibility() {
  var step1_password_button_show = document.getElementById("step1-password-button-show");
  var step1_password_button_hide = document.getElementById("step1-password-button-hide");
  if (step1_password.type === "password") {
    step1_password.type = "text"
    step1_password_button_show.style.display = 'block'
    step1_password_button_hide.style.display = 'none'
  } else {
    step1_password.type = "password"
    step1_password_button_show.style.display = 'none'
    step1_password_button_hide.style.display = 'block'
  }
  step1_password.focus()
}

function step1_button_click() {
  // Check fields
  if (step1_message.value.trim().length == 0) {
    step1_error.innerHTML = "The message cannot be empty."
    step1_error.style.display = 'block';
    return
  }
  if (step1_message.value.trim().length > 1000) {
    step1_error.innerHTML = "The message cannot be greater than 1000 characters."
    step1_error.style.display = 'block';
    return
  }
  if (step1_password.value.length == 0) {
    step1_error.innerHTML = "The password cannot be empty."
    step1_error.style.display = 'block';
    return
  }
  if (step1_password.value.length > 100) {
    step1_error.innerHTML = "The password cannot be greater than 100 characters."
    step1_error.style.display = 'block';
    return
  }
  // Enable loading & disabled status
  step1_button_icon.style.display = 'none';
  step1_button.disabled = true;
  step1_button_loading.style.display = 'inline-block';
  step1_message.readOnly = true;
  step1_password.readOnly = true;
  // Create Cryptex
  fetch('https://api.cryptex.ninja/encrypt',
  {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json',
    }),
    body: JSON.stringify({
      'message': CryptoJS.AES.encrypt(step1_message.value, step1_password.value).toString(),
      'password': CryptoJS.SHA3(step1_password.value).toString(CryptoJS.enc.Hex),
      'retention': "86400",
    }),
  })
  .then((response) => {
    if (response.ok) return response.json();
    return response.text().then(text => { throw new Error(text) });
  })
  .then((data) => {
    step2_url.href = 'https://cryptex.ninja/' + data.id
    step2_url.innerHTML = 'https://cryptex.ninja/' + data.id
    step1.style.display = 'none';
    step2.style.display = 'block';
    step1_error.style.display = 'none';
  })
  .catch((error) => {
    step1_error.innerHTML = error.message
    step1_error.style.display = 'block';
  })
  .finally(() => {
    step1_button.disabled = false;
    step1_button_icon.style.display = 'inherit';
    step1_button_loading.style.display = 'none';
    step1_message.readOnly = false;
    step1_password.readOnly = false;
  })
}

// Step2
function copyURL() {
  navigator.clipboard.writeText(step2_url.href);
  step2_copy_url.innerHTML = 'URL Copied!'
  setTimeout(() => {
    step2_copy_url.innerHTML = 'Copy URL'
  }, 1000)
}

function shareWhatsapp() {
  window.open(encodeURI('https://wa.me/?text=' + step2_url.href), '_blank');
}

function shareTelegram() {
  window.open(encodeURI('tg://msg?text=' + step2_url.href), '_blank');
}

// Step3
step3_password.addEventListener('input', () => {
  step3_password_count.textContent = `${step3_password.value.length} / 100`
  if (step3_password.value.length > 100) step3_password_count.style.color = '#dc3545'
  else step3_password_count.style.color = theme_text.innerHTML == 'Dark' ? '#adb5db' : '#212529'
});

step3_password.addEventListener("keydown", (e) => {
  if (e.code === "Enter") step3_button_click()
});

function togglePassword3Visibility() {
  var step3_password_button_show = document.getElementById("step3-password-button-show");
  var step3_password_button_hide = document.getElementById("step3-password-button-hide");
  if (step3_password.type === "password") {
    step3_password.type = "text"
    step3_password_button_show.style.display = 'block'
    step3_password_button_hide.style.display = 'none'
  } else {
    step3_password.type = "password"
    step3_password_button_show.style.display = 'none'
    step3_password_button_hide.style.display = 'block'
  }
  step3_password.focus()
}

function step3_button_click() {
  if (step3_password.value.length == 0) {
    step3_error.innerHTML = "The password cannot be empty."
    step3_error.style.display = 'block';
    return
  }
  if (step3_password.value.length > 100) {
    step3_error.innerHTML = "The password cannot be greater than 100 characters."
    step3_error.style.display = 'block';
    return
  }
  // Enable loading & disabled status
  step3_button_icon.style.display = 'none';
  step3_button.disabled = true;
  step3_button_loading.style.display = 'inline-block';
  step3_password.readOnly = true;
  // Read Cryptex
  fetch('https://api.cryptex.ninja/decrypt',
  {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json',
    }),
    body: JSON.stringify({
      'id': window.location.pathname.substring(1),
      'password': CryptoJS.SHA3(step3_password.value).toString(CryptoJS.enc.Hex),
    }),
  })
  .then((response) => {
    if (response.ok) return response.json();
    return response.text().then(text => { throw new Error(text) });
  })
  .then((data) => {
    step3.style.display = 'none';
    step3_error.style.display = 'none';
    step4.style.display = 'block';
    step4_message.value = CryptoJS.AES.decrypt(data.message, step3_password.value).toString(CryptoJS.enc.Utf8)
    step4_expiration.value = data.expiration
    // Create a new input event
    var event = new Event('input', {
      bubbles: true,
      cancelable: true,
    });
    // Dispatch the event on the textarea
    step4_message.dispatchEvent(event);
  })
  .catch((error) => {
    step3_error.innerHTML = error.message
    step3_error.style.display = 'block';
    step3_password.focus()
  })
  .finally(() => {
    step3_button.disabled = false;
    step3_button_icon.style.display = 'inherit';
    step3_button_loading.style.display = 'none';
    step3_password.readOnly = false;
  })
}
// Step 4
function copyMessage() {
  navigator.clipboard.writeText(step4_message.value);
  step4_copy_message.innerHTML = 'Message Copied!'
  setTimeout(() => {
    step4_copy_message.innerHTML = 'Copy Message'
  }, 1000)
}
function deleteCryptex() {
  step4_button_delete.style.display = 'none'
  step4_button_delete_confirm.style.display = 'inline'
}
function deleteCryptexConfirm() {
  // Enable loading & disabled status
  step4_button_icon.style.display = 'none';
  step4_button_delete_confirm.disabled = true;
  step4_button_loading.style.display = 'inline-block';
  fetch('https://api.cryptex.ninja/destroy',
  {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json',
    }),
    body: JSON.stringify({
      'id': window.location.pathname.substring(1),
      'password': CryptoJS.SHA3(step3_password.value).toString(CryptoJS.enc.Hex),
    }),
  })
  .then((response) => {
    if (response.ok) return response.json()
    return response.text().then(text => { throw new Error(text) });
  })
  .then(() => {
    step4.style.display = 'none';
    step5.style.display = 'block';
    step4_message_error.style.display = 'none';
  })
  .catch((error) => {
    step4_message_error.innerHTML = error.message
    step4_message_error.style.display = 'block';
  })
  .finally(() => {
    step4_button_delete_confirm.disabled = false;
    step4_button_icon.style.display = 'inherit';
    step4_button_loading.style.display = 'none';
  })
}