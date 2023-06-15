const userInput = document.getElementById('user-input')
const chatLog = document.getElementById('chatlog');
const parser = new DOMParser();
const processingMessageSkeleton = `<div class="mssg new loading badge badge-primary">
                                                <div class="loading-message">
                                                    <span class="spinner-grow spinner-grow-sm" role="status"></span>
                                                    <span class="spinner-grow spinner-grow-sm" role="status"></span>
                                                    <span class="spinner-grow spinner-grow-sm" role="status"></span>
                                                </div>
                                            </div>
                                            `

const processingMessageHtmlDoc = parser.parseFromString(processingMessageSkeleton, 'text/html');
const processingMessageElm = processingMessageHtmlDoc.querySelector('.mssg');


function adjustInputHeight() {
    userInput.style.height = 'auto'; // Reset the height to auto
    userInput.style.height = userInput.scrollHeight + 'px'; // Set the height to fit the content
}


function generateMssgElm(content, personal=true) {
    // send_case(input)
    const mssgSkeleton = `<div class="mssg new ${personal? "personal-message align-self-end": ""}"><p class="mssg-content m-0"></p></div>`;
    // const skeleton = '<div class="mssg new personal-message"><p class="mssg-content m-0"></p></div>';
    const mssgHtmlDoc = parser.parseFromString(mssgSkeleton, 'text/html');
    const mssgElm = mssgHtmlDoc.querySelector('.mssg');
    mssgElm.querySelector('.mssg-content').innerHTML = content.replaceAll('\n', '<br>');
    // let chatboxFixerElm = chatLog.querySelector('#chatbox-fixer')
    // chatLog.insertBefore(mssgElm, chatboxFixerElm);
    return mssgElm
}

// function generateResponse(){
//     const mssgSkeleton = '<div class="mssg new response-message"><ul class="mssg-content m-0"></ul></div>';
//     const mssgHtmlDoc = parser.parseFromString(mssgSkeleton, 'text/html');
//     const mssgElm = mssgHtmlDoc.querySelector('.mssg.response-message');
//     mssgElm.querySelector('.mssg-content').innerHTML = text.replaceAll('\n', '<br>');
//     return mssgElm
// }

function generateDiagnosisMssg(symptoms, disease){
    const mssgSkeleton = `
        <div class="mssg new response-message">
            <div class="mssg-content m-0">
                <h5>Captured symptoms are: </h5>
                <ul id="symptoms-list">
                </ul>
                <h5>Diagnosis: </h5>
                <p id="diagnosis"></p>
                <h5><b>Cautions!</b></h5>
                <p>
                    Please be aware that our symptom checker is intended for informational 
                    purposes only and may not provide accurate diagnoses. It is strongly recommended to consult a qualified 
                    doctor or visit a clinic for a professional evaluation of your symptoms. Your health should always be 
                    prioritized, and seeking medical advice ensures that you receive proper care tailored to your specific 
                    needs.
                </p>
            </div>
            
        </div>
    `
    let mssgHtmlDoc = parser.parseFromString(mssgSkeleton, 'text/html');
    const mssgElm = mssgHtmlDoc.querySelector('.mssg.response-message');
    let symptomsList = mssgElm.querySelector('#symptoms-list')
    let diagnosisMssg = mssgElm.querySelector('#diagnosis')
    diagnosisMssg.innerHTML = disease
    for (let symptom of symptoms)
        symptomsList.appendChild(document.createElement('li')).innerHTML = symptom.replaceAll('_', ' ')
    return mssgElm
}


  

let loadingMessageAppended = false;

function sendMssg(event){
    const delay = 0.3

    if (event.key === 'Enter') {
        event.preventDefault();
        if (event.shiftKey && event.key === 'Enter') {
            event.target.value += '\n';
            return;
        }
        let input = event.target.value;
        if (input == ''){
            // event.preventDefault();
            event.target.value = '';
            adjustInputHeight();
            return;
        }
        setTimeout(()=>{
            send_case(input)
        }, delay*1000)
        generatedMssgElm = generateMssgElm(input)
        chatLog.appendChild(generatedMssgElm)
        // setTimeout( ()=> {
        //     chatLog.appendChild(processingMessageElm)
        //     chatLog.scrollTop = chatLog.scrollHeight;
        // }, delay * 1000);
        requestAnimationFrame(() => {
            if (!loadingMessageAppended) {
              requestAnimationFrame(() => {
                chatLog.appendChild(processingMessageElm);
                chatLog.scrollTop = chatLog.scrollHeight;
                loadingMessageAppended = true;
              });
            } else {
                loadingMessageAppended = false;
                chatLog.appendChild(processingMessageElm);
                chatLog.scrollTop = chatLog.scrollHeight;
            }
          });
        // chatLog.scrollTop = chatLog.scrollHeight;
        event.target.value = ''
        adjustInputHeight()
    }
}

let something;





function send_case(userCase){
    const formdata = new FormData();
    formdata.append('case', userCase)
    fetch('/chatbot/diagnose/', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formdata
    }).then(res => {
        if (res.ok){
            console.log("its ok!!")
            return res.json()
        }
        console.log("it has proceeded!!!!")
        throw {
            error: new Error('Something went wrong'),
            response: res
        };
    }).then(data => {
        let loadingMssgElm = chatLog.querySelector('.mssg.loading')
        result = generateDiagnosisMssg(data.result.symptoms, data.result.diagnosis)
        loadingMssgElm.replaceWith(result)
        chatLog.scrollTop = chatLog.scrollHeight;   
    }).catch(err => {
        err.response.json().then(data => {
            let loadingMssgElm = chatLog.querySelector('.mssg.loading')
            // result = generateMssgElm("Too few symptoms extracted, please provide me with more information.", false)
            result = generateMssgElm(data.message, false)
            loadingMssgElm.replaceWith(result)
            chatLog.scrollTop = chatLog.scrollHeight;   
        })
       
        // console.log("something went wrong: ", err)
    })
}



userInput.addEventListener('input', adjustInputHeight);
userInput.addEventListener('keydown', sendMssg);