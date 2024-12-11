const swiper = new Swiper('.card-wrapper', {
    loop: true,
    spaceBetween: 30,

    
    pagination: {
        el: '.swiper-pagination',
        clickable:true,
        dynamicBullers: true
    },

    // Navigation arrows
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },

    breakpoints: {
        0: {
            slidesPerView: 1
        },
        768: {
            slidesPerView: 2
        },
        992: {
            slidesPerView: 3
        },
        1200: {
            slidesPerView: 4
        }
    }
});