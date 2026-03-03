/**
 * main.js – Interactive effects for AI Compliance Management Platform
 * Features:
 *   - Mobile hamburger menu toggle
 *   - Smooth active nav-link highlighting on scroll
 *   - Scroll-triggered fade-in animations (IntersectionObserver)
 *   - Navbar background elevation on scroll
 */

(function () {
  'use strict';

  /* ── DOM references ─────────────────────────────────────── */
  const navbar     = document.querySelector('.navbar');
  const hamburger  = document.querySelector('.navbar__hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  const navLinks   = document.querySelectorAll('.navbar__link, .navbar__mobile-link');
  const sections   = document.querySelectorAll('section[id]');
  const scrollEls  = document.querySelectorAll('.fade-in-scroll');

  /* ── Mobile menu toggle ─────────────────────────────────── */
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      const isOpen = !mobileMenu.hidden;
      mobileMenu.hidden = isOpen;
      hamburger.setAttribute('aria-expanded', String(!isOpen));

      // Animate hamburger → × 
      const spans = hamburger.querySelectorAll('span');
      if (!isOpen) {
        spans[0].style.transform = 'translateY(7px) rotate(45deg)';
        spans[1].style.opacity   = '0';
        spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity   = '';
        spans[2].style.transform = '';
      }
    });

    // Close mobile menu when a link is clicked
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileMenu.hidden = true;
        hamburger.setAttribute('aria-expanded', 'false');
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity   = '';
        spans[2].style.transform = '';
      });
    });
  }

  /* ── Navbar elevation on scroll ────────────────────────── */
  function onScroll () {
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 4px 24px rgba(0,0,0,0.45)';
    } else {
      navbar.style.boxShadow = '';
    }

    highlightActiveLink();
  }

  /* ── Active nav-link highlighting ──────────────────────── */
  function highlightActiveLink () {
    let current = '';
    sections.forEach(function (section) {
      const sectionTop = section.offsetTop - 80;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(function (link) {
      link.classList.remove('navbar__link--active');
      const href = link.getAttribute('href');
      if (href && href.includes(current) && current !== '') {
        link.classList.add('navbar__link--active');
      }
    });
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // run once on load

  /* ── Scroll-triggered fade-in (IntersectionObserver) ───── */
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target); // animate only once
          }
        });
      },
      { threshold: 0.15 }
    );

    scrollEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback: show immediately for browsers without IntersectionObserver
    scrollEls.forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  /* ── Smooth scroll for anchor links ────────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
