/**
 * NyayVandan — Frontend Application Logic
 * ==========================================
 * Judicial Decision Support System
 * 
 * Handles:
 *   - Page navigation (Landing → Login → Dashboard)
 *   - Dashboard tab switching
 *   - API communication with backend
 *   - Dynamic rendering of analysis results
 * 
 * ⚠️ Advisory system only. No predictions. No automation.
 */

// ===================== CONFIGURATION =====================

const API_BASE = "http://localhost:8000";

// Store last analysis results for cross-tab access
let lastAnalysisResult = null;

// ===================== PAGE NAVIGATION =====================

/**
 * Show a specific page and hide all others.
 * Pages: landingPage, loginPage, dashboardPage
 */
function showPage(pageId) {
    const pages = ["landingPage", "loginPage", "dashboardPage"];
    pages.forEach(p => {
        document.getElementById(p).classList.toggle("hidden", p !== pageId);
    });
    
    // Reset scroll position
    window.scrollTo(0, 0);
}

/**
 * Handle login form submission.
 * ⚠️ No real authentication — UI flow only as per specification.
 */
function handleLogin(event) {
    event.preventDefault();
    // No real auth — just navigate to dashboard
    showPage("dashboardPage");
}

// ===================== DASHBOARD TAB SWITCHING =====================

/**
 * Switch between dashboard tabs: caseAnalysis, ethicalReview, about
 */
function switchTab(tabName) {
    // Hide all tabs
    const tabs = ["tabCaseAnalysis", "tabEthicalReview", "tabAbout"];
    tabs.forEach(t => {
        document.getElementById(t).classList.add("hidden");
    });
    
    // Deactivate all nav items
    const navItems = ["navCaseAnalysis", "navEthicalReview", "navAbout"];
    navItems.forEach(n => {
        document.getElementById(n).classList.remove("active");
    });
    
    // Show selected tab and activate nav
    const tabMap = {
        caseAnalysis: { tab: "tabCaseAnalysis", nav: "navCaseAnalysis" },
        ethicalReview: { tab: "tabEthicalReview", nav: "navEthicalReview" },
        about: { tab: "tabAbout", nav: "navAbout" },
    };
    
    const selected = tabMap[tabName];
    if (selected) {
        document.getElementById(selected.tab).classList.remove("hidden");
        document.getElementById(selected.nav).classList.add("active");
    }
}

// ===================== CASE ANALYSIS =====================

/**
 * Main analysis function — sends case facts to backend API.
 */
async function analyzeCase() {
    const caseText = document.getElementById("caseTextInput").value.trim();
    const topK = parseInt(document.getElementById("topKSelect").value);
    
    // Validation
    if (!caseText || caseText.length < 20) {
        alert("Please enter at least 20 characters of case facts for analysis.");
        return;
    }
    
    // Show loading
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                case_text: caseText,
                top_k: topK
            })
        });
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        lastAnalysisResult = data;
        
        // Render all result panels
        renderEntities(data.extracted_entities);
        renderPrecedents(data.similar_cases);
        renderExplanations(data.explanations);
        renderEthicalReview(data.ethical_flags);
        renderDisclaimer(data.disclaimer);
        
    } catch (error) {
        console.error("Analysis failed:", error);
        alert(`Analysis failed: ${error.message}\n\nMake sure the backend server is running at ${API_BASE}`);
    } finally {
        showLoading(false);
    }
}

// ===================== LOADING OVERLAY =====================

function showLoading(isLoading) {
    const overlay = document.getElementById("loadingOverlay");
    const btn = document.getElementById("btnAnalyze");
    
    overlay.classList.toggle("hidden", !isLoading);
    btn.disabled = isLoading;
    btn.textContent = isLoading ? "⏳ Analyzing..." : "⚖ Analyze Case";
}

// ===================== RENDER: EXTRACTED ENTITIES =====================

function renderEntities(entities) {
    const panel = document.getElementById("entitiesPanel");
    const content = document.getElementById("entitiesContent");
    
    panel.classList.remove("hidden");
    
    let html = '<div style="display: flex; flex-wrap: wrap; gap: var(--spacing-lg);">';
    
    // IPC Sections
    html += renderEntityGroup("IPC Sections", entities.IPC_Sections, "ipc");
    
    // CrPC Sections
    html += renderEntityGroup("CrPC Sections", entities.CrPC_Sections, "crpc");
    
    // Constitutional Articles
    html += renderEntityGroup("Constitutional Articles", entities.Constitutional_Articles, "article");
    
    // Referenced Acts
    if (entities.Acts_Referenced && entities.Acts_Referenced.length > 0) {
        html += renderEntityGroup("Acts Referenced", entities.Acts_Referenced, "act");
    }
    
    html += '</div>';
    
    content.innerHTML = html;
}

function renderEntityGroup(title, items, tagClass) {
    let html = `<div style="flex: 1; min-width: 200px;">`;
    html += `<h4 style="color: var(--text-gold); font-size: 0.88rem; margin-bottom: var(--spacing-sm);">${title}</h4>`;
    
    if (items && items.length > 0) {
        html += '<div style="display: flex; flex-wrap: wrap; gap: 4px;">';
        items.forEach(item => {
            html += `<span class="tag tag-${tagClass}">${escapeHtml(item)}</span>`;
        });
        html += '</div>';
    } else {
        html += '<p class="text-muted" style="font-size: 0.85rem;">None detected</p>';
    }
    
    html += '</div>';
    return html;
}

// ===================== RENDER: SIMILAR PRECEDENTS =====================

function renderPrecedents(cases) {
    const panel = document.getElementById("precedentsPanel");
    const content = document.getElementById("precedentsContent");
    const subtitle = document.getElementById("precedentsSubtitle");
    
    panel.classList.remove("hidden");
    subtitle.textContent = `Found ${cases.length} similar precedent${cases.length !== 1 ? 's' : ''}`;
    
    let html = '';
    
    cases.forEach((c, index) => {
        const simClass = getSimilarityClass(c.similarity_label);
        
        html += `
        <div class="case-card" id="caseCard${index}">
            <div class="case-card-header">
                <div>
                    <span class="case-card-title">${escapeHtml(c.case_title || c.case_id)}</span>
                </div>
                <div class="case-card-meta">
                    <span>🏛 ${escapeHtml(c.court)}</span>
                    <span>📅 ${c.year}</span>
                    <span class="tag tag-similarity ${simClass}">${escapeHtml(c.similarity_label)}</span>
                </div>
            </div>
            <div class="case-card-body">
                <!-- Scores -->
                <div class="case-scores">
                    ${renderScoreBar("Semantic", c.scores.semantic)}
                    ${renderScoreBar("Lexical", c.scores.lexical)}
                    ${renderScoreBar("Entity", c.scores.entity_overlap)}
                    ${renderScoreBar("Overall", c.scores.hybrid)}
                </div>
                
                <!-- Legal Sections -->
                <div class="case-sections">
                    ${renderCaseSections(c)}
                </div>
                
                <!-- Outcome -->
                <div style="margin-top: var(--spacing-md);">
                    <span style="color: var(--text-muted); font-size: 0.82rem;">Outcome: </span>
                    <span style="color: var(--text-primary); font-size: 0.88rem; font-weight: 600;">${escapeHtml(c.judgment_outcome)}</span>
                </div>
                
                <!-- Case Text (expandable) -->
                <div class="case-text-preview" id="caseText${index}" style="margin-top: var(--spacing-md);">
                    ${escapeHtml(c.case_text)}
                    <div class="fade-overlay"></div>
                </div>
                <button class="expand-btn" onclick="toggleCaseText(${index})">
                    <span id="expandIcon${index}">▶</span> View full facts
                </button>
            </div>
        </div>
        `;
    });
    
    content.innerHTML = html;
}

function renderScoreBar(label, score) {
    const pct = Math.round(score * 100);
    return `
    <div class="score-bar-container">
        <span class="score-bar-label">${label}</span>
        <div class="score-bar-track">
            <div class="score-bar-fill" style="width: ${pct}%"></div>
        </div>
        <span class="score-bar-value">${pct}%</span>
    </div>
    `;
}

function renderCaseSections(c) {
    let html = '';
    
    if (c.ipc_sections) {
        c.ipc_sections.split(',').filter(s => s.trim()).forEach(s => {
            html += `<span class="tag tag-ipc">IPC ${escapeHtml(s.trim())}</span>`;
        });
    }
    
    if (c.crpc_sections) {
        c.crpc_sections.split(',').filter(s => s.trim()).forEach(s => {
            html += `<span class="tag tag-crpc">CrPC ${escapeHtml(s.trim())}</span>`;
        });
    }
    
    if (c.constitutional_articles) {
        c.constitutional_articles.split(',').filter(s => s.trim()).forEach(s => {
            html += `<span class="tag tag-article">Art. ${escapeHtml(s.trim())}</span>`;
        });
    }
    
    return html || '<span class="text-muted" style="font-size: 0.82rem;">No specific sections listed</span>';
}

function getSimilarityClass(label) {
    if (!label) return 'tag-low';
    const lower = label.toLowerCase();
    if (lower.includes('highly')) return 'tag-high';
    if (lower.includes('moderate')) return 'tag-moderate';
    return 'tag-low';
}

function toggleCaseText(index) {
    const textEl = document.getElementById(`caseText${index}`);
    const iconEl = document.getElementById(`expandIcon${index}`);
    
    const isExpanded = textEl.classList.toggle('expanded');
    iconEl.textContent = isExpanded ? '▼' : '▶';
}

// ===================== RENDER: EXPLANATIONS =====================

function renderExplanations(explanations) {
    const panel = document.getElementById("explanationsPanel");
    const content = document.getElementById("explanationsContent");
    
    panel.classList.remove("hidden");
    
    let html = '';
    
    explanations.forEach((exp, index) => {
        html += `
        <div class="explanation-card" id="explanation${index}">
            <div class="panel-header">
                <span class="icon">🔍</span>
                <h3>${escapeHtml(exp.case_id)} — ${escapeHtml(exp.similarity_label)}</h3>
            </div>
            
            <!-- Explanation Text -->
            <div class="explanation-text">
                ${escapeHtml(exp.explanation_text)}
            </div>
            
            <!-- Entity Overlap Details -->
            ${renderEntityOverlap(exp.entity_overlap)}
            
            <!-- Influential Terms -->
            ${renderInfluentialTerms(exp.influential_terms)}
            
            <div class="disclaimer" style="margin-top: var(--spacing-md); padding: var(--spacing-sm) var(--spacing-md);">
                <p style="font-size: 0.78rem;">${escapeHtml(exp.disclaimer)}</p>
            </div>
        </div>
        `;
    });
    
    content.innerHTML = html;
}

function renderEntityOverlap(overlap) {
    if (!overlap) return '';
    
    let parts = [];
    
    if (overlap.common_ipc && overlap.common_ipc.length > 0) {
        parts.push(`<div style="margin-bottom: var(--spacing-sm);">
            <span style="color: var(--text-muted); font-size: 0.82rem;">Common IPC:</span> 
            ${overlap.common_ipc.map(s => `<span class="tag tag-ipc">${escapeHtml(s)}</span>`).join(' ')}
        </div>`);
    }
    
    if (overlap.common_crpc && overlap.common_crpc.length > 0) {
        parts.push(`<div style="margin-bottom: var(--spacing-sm);">
            <span style="color: var(--text-muted); font-size: 0.82rem;">Common CrPC:</span> 
            ${overlap.common_crpc.map(s => `<span class="tag tag-crpc">${escapeHtml(s)}</span>`).join(' ')}
        </div>`);
    }
    
    if (overlap.common_articles && overlap.common_articles.length > 0) {
        parts.push(`<div style="margin-bottom: var(--spacing-sm);">
            <span style="color: var(--text-muted); font-size: 0.82rem;">Common Articles:</span> 
            ${overlap.common_articles.map(s => `<span class="tag tag-article">${escapeHtml(s)}</span>`).join(' ')}
        </div>`);
    }
    
    return parts.length > 0 ? `<div style="margin-bottom: var(--spacing-md);">${parts.join('')}</div>` : '';
}

function renderInfluentialTerms(terms) {
    if (!terms || terms.length === 0) return '';
    
    let html = `
    <div style="margin-top: var(--spacing-md);">
        <h4 style="color: var(--text-gold); font-size: 0.88rem; margin-bottom: var(--spacing-sm);">
            Influential Terms
        </h4>
        <div class="terms-grid">
    `;
    
    terms.forEach(t => {
        html += `
        <div class="term-item">
            <span class="term-name">${escapeHtml(t.term)}</span>
            <span class="term-weight">${(t.weight * 100).toFixed(1)}%</span>
        </div>
        `;
    });
    
    html += '</div></div>';
    return html;
}

// ===================== RENDER: ETHICAL REVIEW =====================

function renderEthicalReview(ethicalFlags) {
    if (!ethicalFlags) return;
    
    // Show ethics content, hide placeholder
    document.getElementById("ethicsPlaceholder").classList.add("hidden");
    document.getElementById("ethicsContent").classList.remove("hidden");
    
    // Render diversity score
    renderDiversityScore(ethicalFlags.diversity_score);
    
    // Render bias warnings
    renderBiasWarnings(ethicalFlags.bias_warnings);
    
    // Render constitutional alignment
    renderConstitutionalAlignment(ethicalFlags.constitutional_alignment);
}

function renderDiversityScore(diversity) {
    const content = document.getElementById("diversityContent");
    const overallPct = Math.round(diversity.overall_score * 100);
    const color = overallPct >= 60 ? 'var(--success)' : overallPct >= 30 ? 'var(--accent-gold)' : 'var(--warning)';
    
    let html = `
    <div class="diversity-meter">
        <div class="diversity-score-value" style="color: ${color}">
            ${overallPct}%
        </div>
        <div class="diversity-bar" style="flex: 1;">
            ${renderScoreBar("Court", diversity.court_diversity)}
            ${renderScoreBar("Temporal", diversity.temporal_diversity)}
            ${renderScoreBar("Outcome", diversity.outcome_diversity)}
        </div>
    </div>
    
    <div style="display: flex; flex-wrap: wrap; gap: var(--spacing-md); margin-top: var(--spacing-md);">
        <div style="flex: 1; min-width: 200px;">
            <p class="text-muted" style="font-size: 0.82rem;">Courts Represented</p>
            <div style="margin-top: var(--spacing-xs);">
                ${(diversity.details.courts_represented || []).map(c => 
                    `<span class="tag tag-article" style="margin-bottom: 4px;">${escapeHtml(c)}</span>`
                ).join(' ')}
            </div>
        </div>
        <div>
            <p class="text-muted" style="font-size: 0.82rem;">Year Range</p>
            <p style="color: var(--text-primary); font-size: 0.92rem; margin-top: var(--spacing-xs);">
                ${escapeHtml(diversity.details.year_range || 'N/A')}
            </p>
        </div>
        <div>
            <p class="text-muted" style="font-size: 0.82rem;">Total Cases</p>
            <p style="color: var(--text-primary); font-size: 0.92rem; margin-top: var(--spacing-xs);">
                ${diversity.details.total_cases || 0}
            </p>
        </div>
    </div>
    `;
    
    content.innerHTML = html;
}

function renderBiasWarnings(warnings) {
    const content = document.getElementById("biasContent");
    
    if (!warnings || warnings.length === 0) {
        content.innerHTML = `
        <div class="success-box">
            <p>✅ No significant bias indicators detected in the retrieved precedent set.</p>
        </div>
        `;
        return;
    }
    
    let html = '';
    
    warnings.forEach(w => {
        const severityClass = `severity-${w.severity.toLowerCase()}`;
        html += `
        <div class="warning-box">
            <div style="display: flex; align-items: center; gap: var(--spacing-sm); margin-bottom: var(--spacing-xs);">
                <span class="severity ${severityClass}">${w.severity}</span>
                <span class="warning-title">${escapeHtml(w.type.replace(/_/g, ' '))}</span>
            </div>
            <p class="warning-message">${escapeHtml(w.message)}</p>
            <p class="warning-recommendation">💡 Recommendation: ${escapeHtml(w.recommendation)}</p>
        </div>
        `;
    });
    
    content.innerHTML = html;
}

function renderConstitutionalAlignment(notes) {
    const content = document.getElementById("constitutionalContent");
    
    if (!notes || notes.length === 0) {
        content.innerHTML = `
        <p class="text-muted" style="font-size: 0.88rem;">
            No specific constitutional provisions were identified in the query or retrieved cases.
        </p>
        `;
        return;
    }
    
    let html = '';
    
    notes.forEach(n => {
        html += `
        <div class="constitutional-note">
            <span class="article-label">${escapeHtml(n.article)}</span>
            <p class="principle-text">${escapeHtml(n.principle)}</p>
        </div>
        `;
    });
    
    content.innerHTML = html;
}

// ===================== RENDER: DISCLAIMER =====================

function renderDisclaimer(text) {
    const panel = document.getElementById("disclaimerPanel");
    const textEl = document.getElementById("disclaimerText");
    
    panel.classList.remove("hidden");
    textEl.textContent = "⚠️ " + text;
}

// ===================== UTILITY FUNCTIONS =====================

/**
 * Escape HTML to prevent XSS.
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(String(text)));
    return div.innerHTML;
}

// ===================== KEYBOARD SHORTCUTS =====================

document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to analyze
    if (e.ctrlKey && e.key === 'Enter') {
        const caseInput = document.getElementById('caseTextInput');
        if (document.activeElement === caseInput || !document.getElementById('dashboardPage').classList.contains('hidden')) {
            analyzeCase();
        }
    }
});

// ===================== INITIALIZATION =====================

// Start on landing page
document.addEventListener('DOMContentLoaded', function() {
    showPage('landingPage');
});
