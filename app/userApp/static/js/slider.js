const swiper1 = new Swiper('.slider1',{
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    grabCursor: true,
    loop: true,
    autoplay: {
        delay: 1500,
    },
    breakpoints: {
        970:{
            loop: true,
        },
        10:{
            autoplay: false,
            pagination: false
        },
    }
})

const s2 = document.querySelector('.slider2')
const slidesCount = s2.querySelectorAll('.swiper-slide').length
const sliderPerV = slidesCount <= 3 ? 1 : 4
const sliderPerV960 = sliderPerV == 1 ? 1 : 3
const slidesPerV670 = sliderPerV == 1 ? 1 : 2

const swiper2 = new Swiper('.slider2',{
    navigation: {
        prevEl: '.slider2 .swiper-button-prev',
        nextEl: '.slider2 .swiper-button-next',
    },
    slidesPerView: sliderPerV,
    spaceBetween: 35,
    
    slidesPerGroup: sliderPerV,
    loop: true,
    breakpoints: {
        970:{
            slidesPerView: sliderPerV,
            slidesPerGroup: sliderPerV,
        },
        960:{
            slidesPerView: sliderPerV960,
            slidesPerGroup: sliderPerV960,
        },
        670:{
            slidesPerView: slidesPerV670,
            slidesPerGroup: slidesPerV670,
        },
        10:{
            slidesPerView: 1,
            slidesPerGroup:1,
        },
    }
})

