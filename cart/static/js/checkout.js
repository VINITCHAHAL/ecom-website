let currentIndex = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;
function showSlide(index) {
    const sliderInner = document.querySelector('.slider-inner');
    currentIndex = (index + totalSlides) % totalSlides;
    const offset = -currentIndex * 100;
    sliderInner.style.transform = `translateX(${offset}%)`;
}
function moveSlide(direction) {
    showSlide(currentIndex + direction);
}
