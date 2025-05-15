$(document).ready(function() {
    'use strict';
    
    // Sidebar toggle for mobile/responsive views
    $('#sidebar-toggle').on('click', function() {
        $('.admin-wrapper').toggleClass('sidebar-collapsed');
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        $('.flash-message').fadeOut('slow');
    }, 5000);
    
    // User dropdown menu in topbar
    $('.user-dropdown').on('click', function() {
        $(this).toggleClass('open');
    });
    
    // Close user dropdown when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.user-dropdown').length) {
            $('.user-dropdown').removeClass('open');
        }
    });
    
    // Confirmation dialogs for delete actions
    $('form[data-confirm]').on('submit', function(e) {
        const message = $(this).data('confirm') || 'Are you sure you want to proceed?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    });
    
    // Form validation for required fields
    $('form.needs-validation').on('submit', function(e) {
        const form = $(this);
        let isValid = true;
        
        form.find('[required]').each(function() {
            if (!$(this).val().trim()) {
                isValid = false;
                $(this).addClass('is-invalid');
                
                // Add or show error message
                let errorElement = $(this).next('.invalid-feedback');
                if (!errorElement.length) {
                    $(this).after('<div class="invalid-feedback">This field is required.</div>');
                } else {
                    errorElement.show();
                }
            } else {
                $(this).removeClass('is-invalid');
                $(this).next('.invalid-feedback').hide();
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
    
    // Remove validation error when field is filled
    $('form.needs-validation [required]').on('input', function() {
        if ($(this).val().trim()) {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').hide();
        }
    });
    
    // Image preview for uploads
    $('.custom-file-input').on('change', function() {
        const input = this;
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const preview = $(input).closest('.form-group').find('.image-preview');
                if (preview.length) {
                    preview.attr('src', e.target.result).show();
                } else {
                    $(input).closest('.form-group').append(
                        `<div class="mt-2"><img src="${e.target.result}" class="image-preview" style="max-width: 200px; max-height: 200px;"></div>`
                    );
                }
            }
            
            reader.readAsDataURL(input.files[0]);
            
            // Update file name display
            const fileName = $(this).val().split('\\').pop();
            $(this).next('.custom-file-label').html(fileName);
        }
    });
    
    // Date range picker initialization (if exists)
    if ($.fn.daterangepicker && $('.date-range-picker').length) {
        $('.date-range-picker').daterangepicker({
            opens: 'left',
            autoUpdateInput: false,
            locale: {
                cancelLabel: 'Clear',
                applyLabel: 'Apply',
                format: 'YYYY-MM-DD'
            }
        });
        
        $('.date-range-picker').on('apply.daterangepicker', function(ev, picker) {
            $(this).val(
                picker.startDate.format('YYYY-MM-DD') + ' - ' + 
                picker.endDate.format('YYYY-MM-DD')
            );
        });
        
        $('.date-range-picker').on('cancel.daterangepicker', function() {
            $(this).val('');
        });
    }
    
    // Single date picker initialization (if exists)
    if ($.fn.datepicker && $('.date-picker').length) {
        $('.date-picker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }
    
    // Search functionality for tables
    $('#table-search').on('keyup', function() {
        const value = $(this).val().toLowerCase();
        const table = $(this).data('table');
        
        $(`#${table} tbody tr`).filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
    
    // Status filter for appointments
    $('.status-filter').on('click', function(e) {
        e.preventDefault();
        
        const status = $(this).data('status');
        $('.status-filter').removeClass('active');
        $(this).addClass('active');
        
        if (status === 'all') {
            $('.appointment-row').show();
        } else {
            $('.appointment-row').hide();
            $(`.appointment-row[data-status="${status}"]`).show();
        }
    });
    
    // Set active navigation based on current URL
    const currentPath = window.location.pathname;
    $('.admin-nav a').each(function() {
        const link = $(this).attr('href');
        if (currentPath === link || currentPath.startsWith(link) && link !== '/admin') {
            $(this).parent().addClass('active');
        }
    });
}); 