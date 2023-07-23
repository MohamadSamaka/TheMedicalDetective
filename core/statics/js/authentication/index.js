let formNum = 0;
let nextClick = document.querySelectorAll(".next_button");
let backClick = document.querySelectorAll(".back_button");
let mainForms = document.querySelectorAll(".main");
let stepNumContent = document.querySelectorAll(".step-number-content");

let verifyCodeDigitsElms = document.querySelectorAll('.ver-code-digit')
let verifyCodeBtn = document.querySelector("#verify-code-btn")
let sendCodeBtn = document.querySelector('#send-code-btn')
let invalidCodeWarnning = document.querySelector('#invalid-code')

let redirectButton =  document.querySelector('#redirect-btn')

let verificationCountDown;
let redireactionCountDown;
const verificationTimeElement = document.querySelector('#verification-timer');
const redirectionTimeElement = document.querySelector('#redirection-timer');


const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))


let rawInputs = new FormData();


const validationRules = {
	'fname': /^[a-zA-Z]{1,25}$/,
	'lname': /^[a-zA-Z]{1,25}$/,
	'email': /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/,
	// 'pass': /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}$/,
	// 'pass': /^.{10,}/,
	// 'confirm-pass': /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}$/,
	'confirm-pass': /^.{10,}/,
	'phone-num': /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/,
}


function startRediractionCountDown(){
	let redirectionTimeRemaining = 5;
	redirectionTimeElement.innerText  = `You will be redirected to login page in ${redirectionTimeRemaining}s`;
	redireactionCountDown = setInterval(() => {
		redirectionTimeRemaining--;
		redirectionTimeElement.innerText  = `You will be redirected to login page in ${redirectionTimeRemaining}s`;
		if (redirectionTimeRemaining === 0)
			redirectButton.click()
	  }, 1000);
}

function startverificationCountDown() {
	verificationTimeRemaining = 30;
	verificationTimeElement.innerText  = `Time remaining until code expiration: ${verificationTimeRemaining}s`;
	verifyCodeBtn.textContent = "Verify code";
	verificationTimeElement.classList = "text-muted"

	if(!verificationCountDown){
		verifyCodeBtn.addEventListener('click', verifyCode)
		verificationCountDown = setInterval(() => {
			verificationTimeRemaining--;
			verificationTimeElement.innerText  = `Time remaining until code expiration: ${verificationTimeRemaining}s`;
			if (verificationTimeRemaining === 0)
				verificationIntervalTimeOut();
		  }, 1000);
	}
}


function verificationIntervalTimeOut() {
	clearInterval(verificationCountDown);
	verificationCountDown = null;
	verificationTimeElement.innerText  = 'Code expired';
	verificationTimeElement.className = 'text-danger';
	verifyCodeBtn.textContent = "Resend code";
	verifyCodeBtn.removeEventListener('click', verifyCode);
	verifyCodeBtn.addEventListener('click', reSendCode);	
}

function verifyCode(){
	let targettedRoute  = formType == 1 ? '/signup/confirm-code/' : '/login/confirm-code/';
	if(sharedFormValidation()){
		let input_code = Array.from(verifyCodeDigitsElms).map(elm => elm.value).join("");
		const formdata = new FormData();
		formdata.append('code', input_code);
		fetch(targettedRoute, {
			method: 'POST',
			headers: {'X-CSRFToken': csrftoken},
			body: formdata
		}).then(res => {
			if (res.ok){
				formNum++;
				updateform();
				clearInterval(verificationCountDown);
				verificationCountDown = null;
				if (formType == 1) startRediractionCountDown()
			}
			else{
				invalidCodeWarnning.classList.remove('opacity-0')
				invalidCodeWarnning.classList.add('shake')
			}
		}).catch(err => {
			console.log("something went wrong: ", err)
			valid = false;
		})
	}
}


function sendCode(){
	let valid = true;
	let targettedRoute  = formType == 1 ? '/signup/store-user/' : '/login/send-restore-code/';
	fetch(targettedRoute, {
		method: 'POST',
		headers: {'X-CSRFToken': csrftoken},
		body: rawInputs
	}).then(res => {
		if (res.ok){
			startverificationCountDown();
			return
		}
		throw new Error(`Something went wrong, request status code: ${res.status}`);
	}).catch(err => {
		console.log("error: ", err)
		valid = false;
	})
	if(!valid) return false
	startverificationCountDown();
	return valid;
}

function reSendCode(){
	sendCode();
	startverificationCountDown();
	verifyCodeBtn.removeEventListener('click', reSendCode);
	verifyCodeBtn.addEventListener('click', verifyCode);	
}

function isReqruiedFeildsFilled(inputList){
	let valid = true;
	inputList.forEach(input => {
		if(input.hasAttribute('require')){
			if(!input.value.length){
				valid = false;
				input.classList.add('is-invalid');
			}
		}
	});
	return valid;
}

function sharedFormValidation(){
	var textInputs = document.querySelectorAll(".main.active input");
	var selectMenus = document.querySelectorAll(".main.active select");
    return isReqruiedFeildsFilled(textInputs) && isReqruiedFeildsFilled(selectMenus)
	&& dedicatedValidation(textInputs, selectMenus)
}


// add event listers
nextClick.forEach(function(nextClick_form){
    nextClick_form.addEventListener('click', async ()=>{
		if((formType != 0 || formNum != 0) && !await sharedFormValidation())
				return;
		if(formNum == 1 && !sendCode())
			return;
        formNum++;
        updateform();
        contentchange();
		if(formType == 1) //this will work in sign-up page only
        	progress_forward();
    });
});


// Go back in forms
backClick.forEach(function(backClick_form){
	backClick_form.addEventListener('click',function(){
		formNum--;
		clearInterval(verificationCountDown);
		verificationCountDown = null;
		verificationTimeElement.classList = "text-muted"
		updateform();
		if(formType) //this will work in sign-up page only
			progress_backward();
		if(stepNumContent.length - 1 >= formNum)
			contentchange();
	});
});


function updateform(){
    mainForms.forEach(function(mainform_number){
        mainform_number.classList.remove('active');
    })
    mainForms[formNum].classList.add('active');
} 


function contentchange(){
	if(stepNumContent.length - 1 >= formNum){
		stepNumContent.forEach(function(content){
			content.classList.remove('active'); 
			}); 
			stepNumContent[formNum].classList.add('active');
	}
} 


//verifying code controls

let in1 = document.getElementById('otc-1') //first input digit
function splitNumber(e) {
		let data = e.data || e.target.value; // Chrome doesn't get the e.data, it's always empty, fallback to value then.
		if ( ! data ) return; // Shouldn't happen, just in case.
		if ( data.length === 1 ) return; // Here is a normal behavior, not a paste action.
		
		popuNext(e.target, data);
		//for (i = 0; i < data.length; i++ ) { verifyCodeDigitsElms[i].value = data[i]; }
	}

function popuNext(el, data) {
		el.value = data[0]; // Apply first item to first input
		data = data.substring(1); // remove the first char.
		if ( el.nextElementSibling && el.nextElementSibling.nextElementSibling && data.length ) {
			// Do the same with the next element and next data
			popuNext(el.nextElementSibling.nextElementSibling, data);
		}
};

verifyCodeDigitsElms.forEach(function(input) {
	/**
	 * Control on keyup to catch what the user intent to do.
	 * I could have check for numeric key only here, but I didn't.
	 */
	input.addEventListener('keyup', function(e){
		// Break if Shift, Tab, CMD, Option, Control.
		if (e.keyCode === 16 || e.keyCode == 9 || e.keyCode == 224 || e.keyCode == 18 || e.keyCode == 17) {
			 return;
		}
		
		// On Backspace or left arrow, go to the previous field.
		if (this.previousElementSibling && (e.keyCode === 8 || e.keyCode === 37) && this.previousElementSibling.previousElementSibling && this.previousElementSibling.previousElementSibling.tagName === "INPUT" ) {
			this.previousElementSibling.previousElementSibling.select();
		} else if (this.nextElementSibling && e.keyCode !== 8 && this.nextElementSibling.nextElementSibling) {
			this.nextElementSibling.nextElementSibling.select();
		}
		
		// If the target is populated to quickly, value length can be > 1
		if ( e.target.value.length > 1 ) {
			splitNumber(e);
		}
	});
	
	/**
	 * Better control on Focus
	 * - don't allow focus on other field if the first one is empty
	 * - don't allow focus on field if the previous one if empty (debatable)
	 * - get the focus on the first empty field
	 */
	input.addEventListener('focus', function(e) {
		// If the focus element is the first one, do nothing
		if ( this === in1 ) return;
		
		// If value of input 1 is empty, focus it.
		if ( in1.value == '' ) in1.focus();
		
		// If value of a previous input is empty, focus it.
		// To remove if you don't wanna force user respecting the fields order.
		if ( this.previousElementSibling && this.previousElementSibling.previousElementSibling.value == '' ) {
			this.previousElementSibling.previousElementSibling.focus();
		}
	});
});


/**
 * Handle copy/paste of a big number.
 * It catches the value pasted on the first field and spread it into the inputs.
 */


in1.addEventListener('input', splitNumber);
invalidCodeWarnning.addEventListener("animationend", () => {
	invalidCodeWarnning.classList.remove('shake');
});

