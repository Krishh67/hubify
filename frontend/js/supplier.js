document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('supplier-form');
    const submitBtn = document.getElementById('submit-btn');
    const alertContainer = document.getElementById('alert-container');
    const successCard = document.getElementById('success-card');
    const overlay = document.getElementById('loading-overlay');
    
    document.getElementById('btn-submit-another').addEventListener('click', () => {
        successCard.classList.add('hidden');
        form.classList.remove('hidden');
        form.reset();
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
        
        // Basic required field validation
        const requiredFields = [
            'supplier_name', 'email', 'product_offered', 'category',
            'available_quantity', 'unit', 'unit_price', 'min_order_qty', 'pricing_details',
            'location', 'city', 'state', 'country',
            'delivery_capability', 'delivery_days'
        ];
        
        let isValid = true;
        
        requiredFields.forEach(id => {
            const el = document.getElementById(id);
            const errEl = document.getElementById(`err-${id}`);
            if (!el.value.trim()) {
                el.classList.add('error');
                if (errEl) errEl.classList.add('visible');
                isValid = false;
            } else {
                el.classList.remove('error');
                if (errEl) errEl.classList.remove('visible');
            }
        });

        // Numeric checks
        ['available_quantity', 'unit_price', 'min_order_qty', 'delivery_days'].forEach(id => {
            const el = document.getElementById(id);
            if (el.value && Number(el.value) <= 0) {
                el.classList.add('error');
                const errEl = document.getElementById(`err-${id}`);
                if (errEl) errEl.classList.add('visible');
                isValid = false;
            }
        });

        if (!isValid) {
            showAlert('Please fill in all mandatory fields correctly.', 'error');
            window.scrollTo({ top: 0, behavior: 'smooth' });
            return;
        }

        // Handle 'Other' category
        let finalCategory = document.getElementById('category').value;
        const catOther = document.getElementById('category_other');
        if (finalCategory === 'Other' && catOther && catOther.value.trim() !== '') {
            finalCategory = catOther.value.trim();
        }

        const profileId = localStorage.getItem('profile_id');
        if (!profileId) {
            window.location.href = '/auth';
            return;
        }

        const specsVal = document.getElementById('specs').value.trim();
        const specsDict = specsVal ? { "details": specsVal } : {};

        const certsVal = document.getElementById('certifications').value.trim();
        const certsList = certsVal ? certsVal.split(',').map(c => c.trim()).filter(c => c) : [];

        // Gather payload matching SupplierCreate
        const payload = {
            profile_id: parseInt(profileId, 10),
            supplier_name: document.getElementById('supplier_name').value.trim(),
            email: document.getElementById('email').value.trim(),
            product_offered: document.getElementById('product_offered').value.trim(),
            category: finalCategory,
            specs: specsDict,
            available_quantity: parseFloat(document.getElementById('available_quantity').value),
            unit: document.getElementById('unit').value,
            unit_price: parseFloat(document.getElementById('unit_price').value),
            min_order_qty: parseFloat(document.getElementById('min_order_qty').value),
            pricing_details: document.getElementById('pricing_details').value.trim(),
            location: document.getElementById('location').value.trim(),
            city: document.getElementById('city').value.trim(),
            state: document.getElementById('state').value.trim(),
            country: document.getElementById('country').value.trim(),
            delivery_capability: document.getElementById('delivery_capability').value.trim(),
            delivery_days: parseInt(document.getElementById('delivery_days').value, 10),
            certifications: certsList,
            additional_notes: document.getElementById('additional_notes').value.trim() || null
        };

        submitBtn.disabled = true;
        overlay.classList.remove('pointer-events-none', 'opacity-0');
        overlay.classList.add('opacity-100');

        try {
            const res = await fetch('/api/suppliers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Failed to submit offering');
            }

            const data = await res.json();
            
            // Show success
            form.classList.add('hidden');
            successCard.classList.remove('hidden');
            document.getElementById('record-id-display').textContent = `Ref: SUP-${data.id.toString().padStart(6, '0')}`;
            window.scrollTo({ top: 0, behavior: 'smooth' });

        } catch (error) {
            console.error(error);
            showAlert(error.message, 'error');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } finally {
            submitBtn.disabled = false;
            overlay.classList.add('pointer-events-none', 'opacity-0');
            overlay.classList.remove('opacity-100');
        }
    });

    // Clear errors on input
    document.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('error');
            const errEl = document.getElementById(`err-${this.id}`);
            if (errEl) errEl.classList.remove('visible');
            alertContainer.innerHTML = '';
        });
    });

    function showAlert(msg, type) {
        alertContainer.innerHTML = `
            <div class="p-4 rounded-xl text-sm font-bold flex items-center gap-3 ${
                type === 'error' 
                ? 'bg-red-50 text-red-600 border border-red-100' 
                : 'bg-emerald-50 text-emerald-600 border border-emerald-100'
            }">
                <svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${type === 'error' 
                    ? '<path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"/>' 
                    : '<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"/>'}
                </svg>
                ${msg}
            </div>
        `;
    }
});
