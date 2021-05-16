var swiper = new Swiper('.swiper-container', {
    observer: true,
    observeParents: true,
    spaceBetween: 30,
    loop: true,
    centeredSlides: true,
    effect: 'fade',
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },
});

var infinite = new Waypoint.Infinite({
    element: $('.infinite-container')[0],
    handler: function(direction) {

    },
    offset: 'bottom-in-view',

});