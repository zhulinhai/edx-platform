(function() {
    'use strict';
    console.log('new calc');
    this.Calculator = (function() {

        function Calculator() {
            this.hintButton = $('#calculator_hint');
            this.hintPopup = $('.help');
            this.hintsList = this.hintPopup.find('.hint-item');
            this.selectHint($('#' + this.hintPopup.attr('aria-activedescendant')));
            $('.calc').click(this.toggle);
            $('form#calculator').submit(this.calculate).submit(function(e) {
                return e.preventDefault();
            });
            this.hintButton.click($.proxy(this.handleClickOnHintButton, this));
            this.hintPopup.click($.proxy(this.handleClickOnHintPopup, this));
            this.hintPopup.keydown($.proxy(this.handleKeyDownOnHint, this));
            $('#calculator_wrapper').keyup($.proxy(this.handleKeyUpOnHint, this));
            this.handleClickOnDocument = $.proxy(this.handleClickOnDocument, this);
        }

        Calculator.prototype.KEY = {
            TAB: 9,
            ENTER: 13,
            ESC: 27,
            SPACE: 32,
            LEFT: 37,
            UP: 38,
            RIGHT: 39,
            DOWN: 40
        };

        Calculator.prototype.toggle = function(event) {
            var $calc, $calcWrapper, icon, isExpanded, text;
            event.preventDefault();
            $calc = $('.calc');
            $calcWrapper = $('#calculator_wrapper');
            text = gettext('Open Calculator');
            isExpanded = false;
            icon = 'fa-calculator';
            $('div.calc-main').toggleClass('open');
            if ($calc.hasClass('closed')) {
                $calcWrapper.find('input, a').attr('tabindex', -1);
            } else {
                text = gettext('Close Calculator');
                icon = 'fa-close';
                isExpanded = true;
                $calcWrapper.find('input, a').attr('tabindex', 0);
                setTimeout(function() {
                    return $calcWrapper.find('#calculator_input').focus();
                }, 100);
            }
            $calc.attr({
                'title': text,
                'aria-expanded': isExpanded
            }).find('.utility-control-label').text(text);
            $calc.find('.icon').removeClass('fa-calculator').removeClass('fa-close').addClass(icon);
            return $calc.toggleClass('closed');
        };

        Calculator.prototype.showHint = function() {
            this.hintPopup.addClass('shown').attr('aria-hidden', false);
            return $(document).on('click', this.handleClickOnDocument);
        };

        Calculator.prototype.hideHint = function() {
            this.hintPopup.removeClass('shown').attr('aria-hidden', true);
            return $(document).off('click', this.handleClickOnDocument);
        };

        Calculator.prototype.selectHint = function(element) {
            if (!element || (element && element.length === 0)) {
                element = this.hintsList.first();
            }
            this.activeHint = element;
            this.activeHint.focus();
            return this.hintPopup.attr('aria-activedescendant', element.attr('id'));
        };

        Calculator.prototype.prevHint = function() {
            var prev;
            prev = this.activeHint.prev();
            if (this.activeHint.index() === 0) {
                prev = this.hintsList.last();
            }
            return this.selectHint(prev);
        };

        Calculator.prototype.nextHint = function() {
            var next;
            next = this.activeHint.next();
            if (this.activeHint.index() === this.hintsList.length - 1) {
                next = this.hintsList.first();
            }
            return this.selectHint(next);
        };

        Calculator.prototype.handleKeyDown = function(e) {
            if (e.altKey) {
                return true;
            }
            if (e.keyCode === this.KEY.ENTER || e.keyCode === this.KEY.SPACE) {
                if (this.hintPopup.hasClass('shown')) {
                    this.hideHint();
                } else {
                    this.showHint();
                    this.activeHint.focus();
                }
                e.preventDefault();
                return false;
            }
            return true;
        };

        Calculator.prototype.handleKeyDownOnHint = function(e) {
            if (e.altKey) {
                return true;
            }
            switch (e.keyCode) {
                case this.KEY.ESC:
                    this.hideHint();
                    this.hintButton.focus();
                    e.stopPropagation();
                    return false;
                case this.KEY.LEFT:
                case this.KEY.UP:
                    if (e.shiftKey) {
                        return true;
                    }
                    this.prevHint();
                    e.stopPropagation();
                    return false;
                case this.KEY.RIGHT:
                case this.KEY.DOWN:
                    if (e.shiftKey) {
                        return true;
                    }
                    this.nextHint();
                    e.stopPropagation();
                    return false;
            }
            return true;
        };

        Calculator.prototype.handleKeyUpOnHint = function(e) {
            switch (e.keyCode) {
                case this.KEY.TAB:
                    this.active_element = document.activeElement;
                    if (!$(this.active_element).parents().is(this.hintPopup)) {
                        return this.hideHint();
                    }
            }
        };

        Calculator.prototype.handleClickOnDocument = function() {
            return this.hideHint();
        };

        Calculator.prototype.handleClickOnHintButton = function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (this.hintPopup.hasClass('shown')) {
                this.hideHint();
                return this.hintButton.attr('aria-expanded', false);
            } else {
                this.showHint();
                this.hintButton.attr('aria-expanded', true);
                return this.activeHint.focus();
            }
        };

        Calculator.prototype.handleClickOnHintPopup = function(e) {
            return e.stopPropagation();
        };

        Calculator.prototype.calculate = function() {
            return $.getWithPrefix('/calculate', {
                equation: $('#calculator_input').val()
            }, function(data) {
                return $('#calculator_output').val(data.result).focus();
            });
        };

        return Calculator;

    })();

}).call(this);
