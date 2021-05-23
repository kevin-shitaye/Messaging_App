socket = io.connect('http://127.0.0.1:5000/')

document.querySelector('#btn').addEventListener('click', send)
const p = document.querySelector('p')

function send() {
    socket.emit("Hello world")
    console.log("hello");
}
socket.on('connect', ()=>{
    socket.on('message', (msg)=>{
        p.innerHTML = msg
        console.log(msg);
    })
})
