$(document).ready(function() {
    'use strict';
    
    // Mobile Navigation Toggle
    $('.mobile-nav-toggle').on('click', function() {
        $(this).toggleClass('active');
        $('.main-nav').toggleClass('show');
        $('body').toggleClass('nav-open');
    });
    
    // Sticky header on scroll
    $(window).on('scroll', function() {
        if ($(this).scrollTop() > 100) {
            $('.site-header').addClass('sticky');
        } else {
            $('.site-header').removeClass('sticky');
        }
    });
    
    // Smooth scrolling for anchor links
    $('a[href*="#"]:not([href="#"])').on('click', function() {
        if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && location.hostname === this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 80
                }, 800);
                return false;
            }
        }
    });
    
    // Initialize services hover animation with delay
    $('.service-card').each(function(index) {
        $(this).attr('data-aos', 'fade-up');
        $(this).attr('data-aos-delay', (index * 100).toString());
    });
    
    // Initialize team members animation
    $('.team-member').each(function(index) {
        $(this).attr('data-aos', 'fade-up');
        $(this).attr('data-aos-delay', (index * 100).toString());
    });
    
    // Flash messages auto-hide
    setTimeout(function() {
        $('.flash-message').fadeOut('slow');
    }, 5000);
    
    // Gallery image hover effects
    $('.gallery-item').on('mouseenter', function() {
        $(this).find('img').css('transform', 'scale(1.05)');
    }).on('mouseleave', function() {
        $(this).find('img').css('transform', 'scale(1)');
    });
    
    // Form validation styling
    $('.form-control').on('focus', function() {
        $(this).closest('.form-group').addClass('focused');
    }).on('blur', function() {
        if ($(this).val() === '') {
            $(this).closest('.form-group').removeClass('focused');
        }
    });
    
    // FAQ accordion functionality
    $('.faq-question').on('click', function() {
        $(this).parent().toggleClass('active');
        
        // Toggle the icon
        const icon = $(this).find('.toggle-icon i');
        if ($(this).parent().hasClass('active')) {
            icon.removeClass('fa-plus').addClass('fa-minus');
        } else {
            icon.removeClass('fa-minus').addClass('fa-plus');
        }
    });
    
    // Initialize any filter tabs
    $('.tabs-nav a').on('click', function(e) {
        e.preventDefault();
        const category = $(this).data('category');
        
        // Update active tab
        $('.tabs-nav li').removeClass('active');
        $(this).parent().addClass('active');
        
        // Show items based on category
        if (category === 'all') {
            $('.service-card').show();
        } else {
            $('.service-card').hide();
            $('.service-card[data-category="' + category + '"]').show();
        }
    });
    
    // Process steps animation
    $('.process-step').each(function(index) {
        $(this).attr('data-aos', 'fade-up');
        $(this).attr('data-aos-delay', (index * 100).toString());
    });
});
