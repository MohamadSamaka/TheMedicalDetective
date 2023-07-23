// const forgotPasswordBtn = document.querySelector('#forgot-password-btn')
const firstSignupBtn = document.querySelector('#signup-btn-1');
const resetPasswordBtn = document.querySelector('#reset-password-btn');
const invalidLoginWarning = document.querySelector('#invalid-login-error')

async function dedicatedValidation(textInputs, selectMenus){
	let valid = true;
	textInputs.forEach(input => {
		input.classList.remove('is-invalid');
		switch (input.name) {
			case 'confirm-pass':
				const newPass = document.querySelector('#reset-password-pass');
				if (newPass.value != input.value){
					newPass.classList.add('is-invalid');
					input.classList.add('is-invalid');
					valid = false;
				}
				break;
			default:
				if(!RegexTest(input)){
					input.classList.add('is-invalid');
					valid = false;
				}
		}
		if(valid) rawInputs.append(input.name, input.value);
	});
	return valid;
}


async function login(e) {
	const queryParams = new URLSearchParams(window.location.search);
	const nextParam = queryParams.get('next');
    e.preventDefault();
    if (!(await sharedFormValidation())) return false;
    var emailInput = document.querySelector('#email');
    var passwordInput = document.querySelector('#pass');
	rawInputs.append('next', nextParam)
    rawInputs.append('username', emailInput.value);
    rawInputs.append('password', passwordInput.value);

    fetch('/login/', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: rawInputs,
    }).then(res => {
		console.log(res)
        if (res.ok || res.status === 404) 
			window.location.href = res.url
        else if (res.status === 400)
            return res.json(); // Parse response data as JSON
		else
            throw new Error('Request failed with status ' + res.status);
    }).then(res => {
		
        console.log(res);
		let errors = JSON.parse(res.errors)
		t = JSON.parse(res.errors)
		invalidLoginWarning.innerText = errors.__all__[0].message
		invalidLoginWarning.classList.remove('d-none')
		invalidLoginWarning.classList.remove('opacity-0')
		invalidLoginWarning.classList.add('shake')
		
		console.log();
    }).catch(error => {
		if (error.name === 'FetchError' && error.message === 'Failed to fetch') {
            console.error('Request failed: CSRF token missing');
        } else {
            console.error('Request error:', error);
        }
    });

    rawInputs = new FormData(); // Clearing
}


var loginForm = document.querySelector('#login-btn');
loginForm.addEventListener('click', login);


function goBackToFirstForm(e){
	clearInterval(redireactionCountDown);
	e.preventDefault();
	formNum = 0;
	updateform();
	contentchange();
}



function resetPassword(){
	if(!sharedFormValidation()) return false;
	const newPass = document.querySelector('#reset-password-pass').value;
	const confirmPass = document.querySelector('#reset-confirm-password-pass').value;
	const resetPassForm = new FormData();
	resetPassForm.append('new-pass', newPass);
	resetPassForm.append('confirm-pass', confirmPass);
	fetch('/login/reset-password/', {
		method: 'POST',
		headers: {'X-CSRFToken': csrftoken},
		body: resetPassForm
	}).then(res => {
		console.log("got last result!")
		if (res.ok){
			formNum++;
			// updateform();
			startRediractionCountDown()
			// clearInterval(verificationCountDown);
			// verificationCountDown = null;
			// startRediractionCountDown()
			return res.text();
		}
		console.log("something went wrong")
		return res.text()
	}).then(res => {
		console.log("another: ", res)
	}).catch(err => {
		console.log("error: ", err)
		valid = false;
	})
	console.log("confirming code")
}


// function verifyCode(){
// 	if(!sharedFormValidation()) return false;
// 	const newPass = document.querySelector('#reset-password-pass').value;
// 	const confirmPass = document.querySelector('#confirm-pass').value;
// 	const resetPassForm = new FormData();
// 	formdata.add('new-pass', newPass);
// 	formdata.add('confirm-pass', confirmPass);
// 	formdata.append('code', input_code);
// 	fetch('/login/reset-password/', {
// 		method: 'POST',
// 		headers: {'X-CSRFToken': csrftoken},
// 		body: resetPassForm
// 	}).then(res => {
// 		console.log("got last result!")
// 		if (res.ok){
// 			formNum++;
// 			updateform();
// 			// clearInterval(verificationCountDown);
// 			// verificationCountDown = null;
// 			// startRediractionCountDown()
// 			return res.text();
// 		}
// 		console.log("something went wrong")
// 		return res.text()
// 	}).then(res => {
// 		console.log("another: ", res)
// 	}).catch(err => {
// 		console.log("error: ", err)
// 		valid = false;
// 	})
// 	console.log("confirming code")
// }




function RegexTest(input) {
	return validationRules[input.name]? validationRules[input.name].test(input.value): true
}


// sendCodeBtn.addEventListener('click', sendCode, { capture: true })
redirectButton.addEventListener('click', goBackToFirstForm)
resetPasswordBtn.addEventListener('click', resetPassword)

invalidLoginWarning.addEventListener("animationend", () => {
	invalidLoginWarning.classList.remove('shake');

});