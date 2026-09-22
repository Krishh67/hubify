document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('client-form');
    
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('edit_id');

    if (editId) {
        document.getElementById('submit-btn').textContent = 'Update Requirement';
        fetch(`/api/clients/${editId}`).then(r => r.json()).then(data => {
            for (const key in data) {
                const el = document.getElementById(key);
                if (el) {
                    if (key === 'specs' && data[key] && data[key].details) {
                        el.value = data[key].details;
                    } else if (key === 'certifications' && Array.isArray(data[key])) {
                        el.value = data[key].join(', ');
                    } else if (key === 'category' && !Array.from(el.options).map(o => o.value).includes(data[key])) {
                        el.value = 'Other';
                        document.getElementById('category_other').classList.remove('hidden');
                        document.getElementById('category_other').value = data[key];
                    } else {
                        el.value = data[key];
                    }
                }
            }
        }).catch(e => console.error("Failed to load edit data", e));
    }
    
    // Auto-clear errors on input
    form.querySelectorAll('input, select, textarea').forEach(el => {
        el.addEventListener('input', () => {
            el.classList.remove('error');
            const errSpan = document.getElementById('err-' + el.id);
            if (errSpan) errSpan.classList.remove('visible');
        });
    });

    const categorySelect = document.getElementById('category');
    const categoryOther = document.getElementById('category_other');
    if (categorySelect && categoryOther) {
        categorySelect.addEventListener('change', () => {
            if (categorySelect.value === 'Other') {
                categoryOther.classList.remove('hidden');
                categoryOther.required = true;
            } else {
                categoryOther.classList.add('hidden');
                categoryOther.required = false;
                categoryOther.value = '';
            }
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset errors
        form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        form.querySelectorAll('.field-error').forEach(el => el.classList.remove('visible'));
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const catSelect = document.getElementById('category');
        const catOther = document.getElementById('category_other');
        if (catSelect.value === 'Other' && catOther.value.trim() !== '') {
            data.category = catOther.value.trim();
        }

        // Validation
        let isValid = true;
        const requiredFields = ['client_name', 'email', 'product_requirement', 'category', 'quantity_required', 'unit', 'budget', 'location', 'city', 'state', 'country', 'delivery_timeline', 'delivery_days'];
        
        requiredFields.forEach(field => {
            if (!data[field] || data[field].toString().trim() === '') {
                showError(field);
                isValid = false;
            }
        });
        
        if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
            showError('email');
            isValid = false;
        }
        
        if (data.quantity_required && parseFloat(data.quantity_required) <= 0) {
            showError('quantity_required');
            isValid = false;
        }

        if (data.budget && parseFloat(data.budget) < 0) {
            showError('budget');
            isValid = false;
        }

        if (data.delivery_days && parseInt(data.delivery_days) <= 0) {
            showError('delivery_days');
            isValid = false;
        }

        if (!isValid) return;

        // Clean optional fields
        const specsVal = data.specs ? data.specs.toString().trim() : '';
        data.specs = specsVal ? { "details": specsVal } : {};
        
        const certsVal = data.certifications ? data.certifications.toString().trim() : '';
        data.certifications = certsVal ? certsVal.split(',').map(c => c.trim()).filter(c => c) : [];
        
        if (!data.additional_notes) data.additional_notes = null;

        // Numeric conversion
        data.quantity_required = parseFloat(data.quantity_required);
        data.budget = parseFloat(data.budget);
        data.delivery_days = parseInt(data.delivery_days);

        const profileId = localStorage.getItem('profile_id');
        if (!profileId) {
            window.location.href = '/auth';
            return;
        }
        data.profile_id = parseInt(profileId, 10);

        // Submit
        const submitBtn = document.getElementById('submit-btn');
        const overlay = document.getElementById('loading-overlay');
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        overlay.classList.remove('pointer-events-none', 'opacity-0');
        overlay.classList.add('opacity-100');

        const endpointUrl = editId ? `/api/clients/${editId}` : '/api/clients';
        const fetchMethod = editId ? 'PUT' : 'POST';

        try {
            const response = await fetch(endpointUrl, {
                method: fetchMethod,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                form.classList.add('hidden');
                document.getElementById('success-card').classList.remove('hidden');
                document.getElementById('record-id-display').textContent = `Ref: #${result.id}`;
            } else {
                let errorMsg = 'Failed to submit requirement.';
                if (result.detail) {
                    errorMsg = Array.isArray(result.detail) ? result.detail.map(d => d.msg).join(', ') : result.detail;
                }
                showAlert(errorMsg, 'error');
            }
        } catch (error) {
            showAlert('Network error. Please ensure the server is running.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Initialize Requirement';
            overlay.classList.remove('opacity-100');
            overlay.classList.add('opacity-0', 'pointer-events-none');
        }
    });

    document.getElementById('btn-submit-another').addEventListener('click', () => {
        form.reset();
        document.getElementById('success-card').classList.add('hidden');
        form.classList.remove('hidden');
        document.getElementById('alert-container').innerHTML = '';
    });
});

function showError(fieldId) {
    const el = document.getElementById(fieldId);
    const errSpan = document.getElementById('err-' + fieldId);
    if (el) el.classList.add('error');
    if (errSpan) errSpan.classList.add('visible');
}

function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    const color = type === 'error' ? 'red' : 'emerald';
    const bg = type === 'error' ? 'bg-red-500/10' : 'bg-emerald-500/10';
    const border = type === 'error' ? 'border-red-500/20' : 'border-emerald-500/20';
    const text = type === 'error' ? 'text-red-400' : 'text-emerald-400';
    
    const icon = type === 'error' 
        ? `<svg class="w-4 h-4 text-red-400 mt-0.5" viewBox="0 0 24 24" fill="none"><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`
        : `<svg class="w-4 h-4 text-emerald-400 mt-0.5" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;

    container.innerHTML = `
        <div class="p-4 rounded-xl ${bg} border ${border} flex items-start gap-3">
            ${icon}
            <div class="text-[13px] ${text} font-medium">${message}</div>
        </div>
    `;
    
    // Auto dismiss after 5s
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}
