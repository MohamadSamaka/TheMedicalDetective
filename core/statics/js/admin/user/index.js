var updateGeneralInfoBtn = $('#update-general-info-btn')
var profileForm = $('#profile-form')
var emailInput = $("#id_email")
var previousEmail = emailInput.val()
var modal = $("#exampleModal");
var verifyCodeDigitsElms = document.querySelectorAll('.ver-code-digit')
var invalidCodeWarnning = document.querySelector('#invalid-code')
var in1 = document.getElementById('otc-1') //first input digit
var verificationCodeBtn = $('#confirm-code')
var verificationTimerElement = $('#verification-timer')
var verificationTimeRemaining = 30;
var verificationCountDown;

async function doesEmailExist(){
    var newVal = emailInput.val()
    var exist = false
    fdata = new FormData();
	fdata.append('email', newVal);
    
    await fetch('/user/email-exists',{
		method: 'POST',
		body: fdata,
        headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()},
	}).then(res => {
		if(res.status == 409){ //conflict status code
            var errorMessage = $('#error_1_id_email');
            if (errorMessage.length === 0) {
                var errorMessage = $('<span>', {
                    id: 'error_1_id_email',
                    class: 'invalid-feedback',
                    html: '<strong>Custom user with this Email already exists.</strong>'
                  });
                  $('#id_email').after(errorMessage);
            }
            emailInput.addClass('is-invalid');
			exist = true;
		}
		else{
			emailInput.removeClass('is-invalid');
		}        
	}).catch(err => {
		console.log("Erorr: ", err)
	})
	return exist;
}

updateGeneralInfoBtn.on('click', async e => {
    e.preventDefault();

    var newVal = emailInput.val()
    if(previousEmail == newVal){
        var button = document.createElement("button");
        button.setAttribute("type", "submit");
        var form = document.getElementById("profile-form");
        form.appendChild(button);
        button.click();
        form.removeChild(button); 
    }else{
        if(!(await doesEmailExist())){
            sendCode()
        }
    }
})



function startverificationCountDown() {
	verificationTimeRemaining = 30;
	verificationTimerElement.text(`Time remaining until code expiration: ${verificationTimeRemaining}s`)
	verificationCodeBtn.text("Verify code");
	verificationTimerElement.addClass("text-muted")
    verificationTimerElement.removeClass("text-danger")

	if(!verificationCountDown){
		verificationCodeBtn.on('click', verifyCode)
		verificationCountDown = setInterval(() => {
			verificationTimeRemaining--;
			verificationTimerElement.text(`Time remaining until code expiration: ${verificationTimeRemaining}s`);
			if (verificationTimeRemaining === 0)
				verificationIntervalTimeOut();
		  }, 1000);
	}
}


function verificationIntervalTimeOut() {
	clearInterval(verificationCountDown);
	verificationCountDown = null;
	verificationTimerElement.text('Code expired');
	verificationTimerElement.addClass('text-danger');
    verificationTimerElement.removeClass('text-muted')
	verificationCodeBtn.text("Resend code");
    $(verificationCodeBtn).off('click', verifyCode);
    $(verificationCodeBtn).on('click', function() {
        $("#update-general-info-btn").click();
      });
}



function verifyCode(){
	var input_code = Array.from(verifyCodeDigitsElms).map(elm => elm.value).join("");
    const formdata = new FormData();
    formdata.append('code', input_code);
  

    fetch('/user/verify-code', {
        method: 'POST',
        headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()},
        body: formdata
    }).then(res =>{
        if(res.ok)
            return res.text()
            throw {
                status: res.status,
                message: `Something went wrong: ${res.error}`
            };
    })
    .then(body=>{
        document.open();
        document.write(body);
        document.close();
    })
    .catch(err => {
        if(err.status == 401){
            invalidCodeWarnning.classList.remove('opacity-0')
            invalidCodeWarnning.classList.add('shake')
        }
    })
}


function sendCode(){
	var valid = true;
    const formdata = new FormData();

    formdata.append('first_name', $('#id_first_name').val())
    formdata.append('last_name', $('#id_last_name').val())
    formdata.append('email', $('#id_email').val())
	fetch('/user/send-code', {
		method: 'POST',
        headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()},
		body: formdata
	}).then(res => {
        console.log(res)
        if(res.ok) return
        valid = false;
        return res.text()
	}).then(dom =>{
        if (!dom) return;
        document.open();
        document.write(dom);
        document.close();
    })
    .catch(err => {
        console.log("here is your error:")
		console.log("error: ", err)
		valid = false;
	})
	if(!valid) return false
    $(modal).modal("show");
	startverificationCountDown();
	return valid;
}


function splitNumber(e) {
		var data = e.data || e.target.value; // Chrome doesn't get the e.data, it's always empty, fallback to value then.
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



in1.addEventListener('input', splitNumber);
invalidCodeWarnning.addEventListener("animationend", () => {
	invalidCodeWarnning.classList.remove('shake');
});

verificationCodeBtn.on('click', verifyCode)

$(modal).on('hide.bs.modal', function (e) {
    for(let elm of verifyCodeDigitsElms)
        elm.value = ""
    invalidCodeWarnning.classList.add('opacity-0')
    verificationTimerElement.text(`Time remaining until code expiration: ${verificationTimeRemaining}s`);
    verificationTimerElement.addClass('text-muted')
    verificationTimerElement.removeClass('text-danger')
  })