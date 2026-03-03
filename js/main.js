/**
 * main.js – Interactive effects for AI Compliance Management Platform
 * Features:
 *   - Mobile hamburger menu toggle
 *   - Smooth active nav-link highlighting on scroll
 *   - Scroll-triggered fade-in animations (IntersectionObserver)
 *   - Navbar background elevation on scroll
 *   - Counter animation for statistics section
 *   - FAQ accordion (expand / collapse)
 */

(function () {
  'use strict';

  /* ── DOM references ─────────────────────────────────────── */
  const navbar     = document.querySelector('.navbar');
  const hamburger  = document.querySelector('.navbar__hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  const navLinks   = document.querySelectorAll('.navbar__link, .navbar__mobile-link');
  const sections   = document.querySelectorAll('section[id]');

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
  // Threshold: element is 12% visible before triggering; lower than 0.15 default
  // so tall cards on small viewports still animate in reliably.
  var FADE_THRESHOLD = 0.12;

  function observeScrollEls () {
    // `.is-observed` guard prevents double-observing on a static page. If
    // elements were dynamically added and removed, callers should remove the
    // class before re-adding the element to the DOM.
    const scrollEls = document.querySelectorAll('.fade-in-scroll:not(.is-observed)');
    if (!('IntersectionObserver' in window)) {
      scrollEls.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: FADE_THRESHOLD }
    );

    scrollEls.forEach(function (el) {
      el.classList.add('is-observed');
      observer.observe(el);
    });
  }

  observeScrollEls(); // observe all .fade-in-scroll elements currently in the DOM

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

  /* ── Counter animation ──────────────────────────────────── */
  /**
   * Animates a numeric counter from 0 to the target value.
   * Reads `data-target` (number) and `data-suffix` (e.g. "%", "+", "M+") from the element.
   */
  function animateCounter (el) {
    const target  = parseFloat(el.getAttribute('data-target'));
    const suffix  = el.getAttribute('data-suffix') || '';
    const isFloat = target % 1 !== 0;
    const duration = 1800; // ms
    const startTime = performance.now();

    function step (now) {
      const elapsed  = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = target * ease;
      el.textContent = (isFloat ? current.toFixed(1) : Math.floor(current)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  // Trigger counters when stats section enters viewport
  const statsSection = document.getElementById('statistics');
  if (statsSection && 'IntersectionObserver' in window) {
    const counterEls = statsSection.querySelectorAll('[data-target]');
    let countersRun  = false;

    const statsObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !countersRun) {
          countersRun = true;
          counterEls.forEach(function (el) { animateCounter(el); });
          statsObserver.disconnect();
        }
      });
    }, { threshold: 0.3 });

    statsObserver.observe(statsSection);
  }

  /* ── FAQ Accordion ──────────────────────────────────────── */
  /**
   * Shared helper: animate-collapse a FAQ body element to max-height 0.
   * @param {HTMLElement} body - The element to collapse
   */
  function collapseFaqBody (body) {
    body.style.maxHeight = body.scrollHeight + 'px';
    body.classList.add('is-animating');
    body.removeAttribute('hidden');
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        body.style.transition = 'max-height 0.35s ease';
        body.style.maxHeight  = '0';
        body.addEventListener('transitionend', function handler () {
          body.style.transition = '';
          body.style.maxHeight  = '';
          body.classList.remove('is-animating');
          body.setAttribute('hidden', '');
          body.removeEventListener('transitionend', handler);
        });
      });
    });
  }

  /**
   * Each FAQ item has:
   *   .faq-item__trigger  (button, aria-expanded)
   *   .faq-item__body     (div, toggled with hidden attr + smooth animation)
   */
  document.querySelectorAll('.faq-item__trigger').forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
      const bodyId     = trigger.getAttribute('aria-controls');
      const body       = document.getElementById(bodyId);
      if (!body) return;

      if (isExpanded) {
        // Collapse this item
        trigger.setAttribute('aria-expanded', 'false');
        collapseFaqBody(body);
      } else {
        // Expand — close any other open items first (directly, without simulating clicks)
        document.querySelectorAll('.faq-item__trigger[aria-expanded="true"]').forEach(function (other) {
          if (other === trigger) return;
          const otherId   = other.getAttribute('aria-controls');
          const otherBody = document.getElementById(otherId);
          if (!otherBody) return;
          other.setAttribute('aria-expanded', 'false');
          collapseFaqBody(otherBody);
        });

        trigger.setAttribute('aria-expanded', 'true');
        body.classList.add('is-animating');
        body.removeAttribute('hidden');
        body.style.maxHeight  = '0';
        body.style.overflow   = 'hidden';
        requestAnimationFrame(function () {
          body.style.transition = 'max-height 0.35s ease';
          body.style.maxHeight  = body.scrollHeight + 'px';
          body.addEventListener('transitionend', function handler () {
            body.style.transition = '';
            body.style.maxHeight  = '';
            body.style.overflow   = '';
            body.classList.remove('is-animating');
            body.removeEventListener('transitionend', handler);
          });
        });
      }
    });
  });

  /* ── CTA form – prevent default submission ──────────────── */
  const ctaForm = document.querySelector('.cta-section__form');
  if (ctaForm) {
    ctaForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const input = ctaForm.querySelector('.cta-section__input');
      if (input && input.value) {
        input.value = '';
        const btn = ctaForm.querySelector('.cta-section__btn');
        const original = btn.textContent;
        btn.textContent = '✓ Subscribed!';
        btn.style.background = '#22c55e';
        setTimeout(function () {
          btn.textContent = original;
          btn.style.background = '';
        }, 3000);
      }
    });
  }

  /* ── Contact form – prevent default submission ──────────── */
  const contactForm = document.querySelector('.contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = contactForm.querySelector('.contact-form__submit');
      const original = btn.textContent;
      btn.textContent = '✓ Message Sent!';
      btn.style.background = '#22c55e';
      contactForm.reset();
      setTimeout(function () {
        btn.textContent = original;
        btn.style.background = '';
      }, 3500);
    });
  }

})();
