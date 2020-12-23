const show_btn = document.querySelector('.my_open');
const close_btn = document.querySelector('.my_close')
const close_block = document.querySelector('.my_blank')
const log = document.querySelector('.my_login');

show_btn.addEventListener('click', () => {
    //close_block.style.display = 'none'
    log.style.display = 'block'
})

close_btn.addEventListener('click', () => {
    log.style.display = 'none'
    close_block.style.display = 'block'
})


// const colors = ['red','yellow','black','white','blue','green','orange','gray']


// function getRandomIntInclusive(min, max) {
//     min = Math.ceil(min);
//     max = Math.floor(max);
//     return Math.floor(Math.random() * (max - min + 1)) + min; //Максимум и минимум включаются
//   }

// $(document).ready(function(){
//     $('.search_button').click(function(){
//         $(".search_result").css('background-color', colors[getRandomIntInclusive(0,7)])
//     })

// })





// const search_btn = document.querySelector('.search_button')
// const search_res = document.querySelector('.search_result')
// search_btn.addEventListener('click', () => {
//     search_res.style.width = '100px'
//     search_res.style.height = '200px'
// })