let activeTabId = 'tab-clients';

document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    document.querySelector(`[data-target="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
    activeTabId = tabId;
}

async function loadDashboard() {
    buildSkeletons(4);
    
    try {
        const [clientsRes, suppliersRes, matchesRes] = await Promise.all([
            fetch('/api/clients').catch(() => ({ ok: false })),
            fetch('/api/suppliers').catch(() => ({ ok: false })),
            fetch('/api/matches').catch(() => ({ ok: false }))
        ]);

        const clients = clientsRes.ok ? await clientsRes.json() : [];
        const suppliers = suppliersRes.ok ? await suppliersRes.json() : [];
        const matches = matchesRes.ok ? await matchesRes.json() : [];
        
        const uniqueMatchedRequests = new Set(matches.map(m => m.client_id)).size;

        updateStats(clients.length, suppliers.length, uniqueMatchedRequests);
        
        renderClients(clients);
        renderSuppliers(suppliers);
        renderMatches(matches);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        document.querySelectorAll('.tab-pane > div').forEach(el => {
            el.innerHTML = `
                <div class="data-card rounded-2xl p-10 text-center border border-red-100 bg-red-50">
                    <svg class="w-10 h-10 mx-auto mb-4 text-red-500" viewBox="0 0 24 24" fill="none"><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                    <p class="font-bold text-[15px] text-red-600">Failed to connect to the server.</p>
                </div>`;
        });
    }
}

function updateStats(cCount, sCount, mCount) {
    document.getElementById('stat-clients').textContent = cCount;
    document.getElementById('stat-suppliers').textContent = sCount;
    document.getElementById('stat-matches').textContent = mCount;

    document.getElementById('badge-clients').textContent = cCount;
    document.getElementById('badge-suppliers').textContent = sCount;
    document.getElementById('badge-matches').textContent = mCount;
}

function getEmptyState(message) {
    return `
        <div class="data-card rounded-2xl p-16 text-center col-span-full border border-slate-200 bg-slate-50">
            <div class="w-14 h-14 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center mx-auto mb-5">
                <svg class="w-6 h-6 text-slate-400" viewBox="0 0 24 24" fill="none">
                    <path d="M20 12H4M12 4v16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <p class="text-slate-600 text-[15px] font-bold">${message}</p>
        </div>
    `;
}

function renderClients(clients) {
    const container = document.getElementById('clients-list');
    if (!clients || clients.length === 0) {
        container.innerHTML = getEmptyState('No client requirements found.');
        return;
    }

    container.innerHTML = clients.map(client => `
        <div class="data-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-5 bg-white">
            <div>
                <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-slate-900 font-extrabold text-[16px]">${client.client_name}</h3>
                    <span class="text-[10px] bg-blue-50 text-blue-600 border border-blue-100 px-2.5 py-0.5 rounded-full uppercase tracking-wider font-bold">${client.category}</span>
                </div>
                <p class="text-[14px] font-medium text-slate-500 mb-3 truncate max-w-xl">${client.product_requirement}</p>
                <div class="flex items-center gap-5 text-[12px] font-medium text-slate-500">
                    <span class="flex items-center gap-1.5"><svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" stroke="currentColor" stroke-width="2"/><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" stroke="currentColor" stroke-width="2"/></svg> ${client.city}, ${client.country}</span>
                    <span class="flex items-center gap-1.5"><svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/></svg> ${client.delivery_days} Days</span>
                </div>
            </div>
            <div class="text-left md:text-right">
                <div class="text-[18px] font-extrabold text-slate-900 mb-1">${client.quantity_required.toLocaleString()} <span class="text-[13px] font-semibold text-slate-500">${client.unit}</span></div>
                <div class="text-[14px] font-bold text-emerald-600">₹${client.budget.toLocaleString()}</div>
            </div>
        </div>
    `).join('');
}

function renderSuppliers(suppliers) {
    const container = document.getElementById('suppliers-list');
    if (!suppliers || suppliers.length === 0) {
        container.innerHTML = getEmptyState('No suppliers registered in network.');
        return;
    }

    container.innerHTML = suppliers.map(supplier => `
        <div class="data-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-5 bg-white">
            <div>
                <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-slate-900 font-extrabold text-[16px]">${supplier.supplier_name}</h3>
                    <span class="text-[10px] bg-emerald-50 text-emerald-600 border border-emerald-100 px-2.5 py-0.5 rounded-full uppercase tracking-wider font-bold">${supplier.category}</span>
                </div>
                <p class="text-[14px] font-medium text-slate-500 mb-3 truncate max-w-xl">${supplier.product_offered}</p>
                <div class="flex items-center gap-5 text-[12px] font-medium text-slate-500">
                    <span class="flex items-center gap-1.5"><svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" stroke="currentColor" stroke-width="2"/><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" stroke="currentColor" stroke-width="2"/></svg> ${supplier.city}, ${supplier.country}</span>
                    <span class="flex items-center gap-1.5"><svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/></svg> ${supplier.delivery_days} Days</span>
                </div>
            </div>
            <div class="text-left md:text-right">
                <div class="text-[18px] font-extrabold text-slate-900 mb-1">${supplier.available_quantity.toLocaleString()} <span class="text-[13px] font-semibold text-slate-500">${supplier.unit}</span></div>
                <div class="text-[14px] font-bold text-indigo-600">₹${supplier.unit_price.toLocaleString()} / unit</div>
            </div>
        </div>
    `).join('');
}

function renderMatches(matches) {
    const container = document.getElementById('matches-list');
    if (!matches || matches.length === 0) {
        container.innerHTML = getEmptyState('No AI matches generated yet.');
        return;
    }
    
    matches.sort((a, b) => b.final_score - a.final_score);

    container.innerHTML = matches.map(m => {
        const cli = m.clients || {};
        const supp = m.suppliers || {};
        const isHigh = m.final_score > 80;
        const isMed = m.final_score > 50 && !isHigh;
        const scoreColor = isHigh ? 'text-emerald-600' : (isMed ? 'text-amber-500' : 'text-red-500');
        
        return `
        <div class="data-card rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-5 bg-white hover:border-violet-300 transition-colors">
            <div class="flex-1">
                <div class="flex items-center justify-between mb-4">
                    <span class="text-[10px] bg-violet-50 text-violet-600 border border-violet-100 px-2.5 py-0.5 rounded-full uppercase tracking-wider font-bold">AI Match</span>
                    <div class="text-right">
                        <div class="text-2xl font-black ${scoreColor} tracking-tighter leading-none">${m.final_score}<span class="text-sm text-slate-400 font-bold ml-0.5">/100</span></div>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div class="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-2">Client Requirement</div>
                        <div class="font-bold text-slate-900 text-sm mb-1">${cli.product_requirement || 'Unknown'}</div>
                        <div class="text-[12px] font-medium text-slate-500">${cli.quantity_required} ${cli.unit} • ₹${cli.budget}</div>
                    </div>
                    
                    <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div class="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-2">Supplier Offering</div>
                        <div class="font-bold text-slate-900 text-sm mb-1">${supp.product_offered || 'Unknown'}</div>
                        <div class="text-[12px] font-medium text-slate-500">${supp.available_quantity} ${supp.unit} • ₹${supp.unit_price}/${supp.unit}</div>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

function buildSkeletons(n) {
    const html = Array(n).fill(`
        <div class="data-card rounded-2xl p-6 bg-white border border-slate-200">
            <div class="flex items-center gap-4 mb-4">
                <div class="h-5 w-40 skeleton-box"></div>
                <div class="h-5 w-20 skeleton-box rounded-full"></div>
            </div>
            <div class="h-4 w-3/4 skeleton-box mb-5"></div>
            <div class="flex items-center justify-between">
                <div class="h-4 w-32 skeleton-box"></div>
                <div class="h-5 w-24 skeleton-box"></div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('clients-list').innerHTML = html;
    document.getElementById('suppliers-list').innerHTML = html;
    document.getElementById('matches-list').innerHTML = html;
}
