let num = document.querySelector(".step-number");
let stepsList = document.querySelectorAll(".progress-point li");

function redirectToLogin(e){
	clearInterval(redireactionCountDown);
	e.preventDefault();
	window.location.href = "/login";
}

function progress_forward(){
    num.innerHTML = formNum+1;
    stepsList[formNum].classList.add('active');
}  

function progress_backward(){
    var form_num = formNum+1;
    stepsList[form_num].classList.remove('active');
    num.innerHTML = form_num;
} 


function calculateAge(dateString) {
    let today = new Date();
    let birthDate = new Date(dateString);
    let age = today.getFullYear() - birthDate.getFullYear();
    let monthDifference = today.getMonth() - birthDate.getMonth();
    if (monthDifference < 0 || (monthDifference === 0 && today.getDate() < birthDate.getDate()))
		age--;
    return parseInt(age);
}


function RegexTest(input) {
	return validationRules[input.name]? validationRules[input.name].test(input.value): true
}


async function dedicatedValidation(textInputs, selectMenus = []){
	let valid = true;
	textInputs.forEach(input => {
		input.classList.remove('is-invalid');
		switch (input.name) {
			case "bdate":
				let age = calculateAge(input.value)
				if(age > 120 || age <= 6){
					input.classList.add('is-invalid');
					valid = false;					}
				break;
			case "confirm-pass":
				const pass = document.querySelector("#pass-input");
				if (pass.value != input.value){
					input.classList.add('is-invalid');
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

	selectMenus.forEach(input => {
		rawInputs.append(input.name, input.value);
	});

	var emailInput = document.querySelector("#email-input")
	if(!emailInput.classList.contains('is-invalid') && (await isEmailAlreadyExist(emailInput))){
		return false
	}
	return valid;
}


async function isEmailAlreadyExist(emailInput){
	let exist = false;
	// if(formNum == 0){
	fdata = new FormData();
	// emailInput = document.querySelector("#email-input")
	fdata.append('email', emailInput.value);
	await fetch('/signup/email-exists/',{
		method: 'POST',
		body: fdata,
		headers: {"X-CSRFToken": csrftoken}
	}).then(res => {
		if(res.status == 409){ //conflict status code
			emailInput.classList.add('is-invalid');
			emailInput.nextElementSibling.innerText = "This email is already registered";
			exist = true;
		}
		else{
			emailInput.classList.remove('is-invalid');
			emailInput.nextElementSibling.innerText = "";
		}
	}).catch(err => {
		console.log("Erorr: ", err)
	})
	return exist;
}


// sendCodeBtn.addEventListener('click', sendCode, { capture: true })
redirectButton.addEventListener('click', redirectToLogin)
