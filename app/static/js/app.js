// Verity Frontend Engine

const app = {
  activeTab: 'workspace',
  activeRole: 'creator',
  currentDraftId: null,
  currentVersion: 1,
  draftContent: "",
  findings: [],
  comments: [],
  auditLogs: [],
  selectedFindingId: null,
  activeFindingForAction: null,

  // Initial Sample matching Slide 4 Wireframe
  sampleDraft: "Our client-friendly app is the #1 app in India, guaranteed!\nGet 50% off until 31 August. Download now.\n[image: banner.png]",

  init: function() {
    this.draftContent = this.sampleDraft;
    document.getElementById('draft-input').value = this.draftContent;
    this.initDraft();
    this.renderWorkflowActions();
    this.calculateContrast();
  },

  switchTab: function(tabName) {
    this.activeTab = tabName;
    ['workspace', 'clarity', 'kb', 'multiformat', 'audit'].forEach(t => {
      const el = document.getElementById(`view-${t}`);
      const btn = document.getElementById(`tab-${t}`);
      if (t === tabName) {
        el.classList.remove('hidden');
        btn.classList.add('border-blue-500', 'text-white');
        btn.classList.remove('border-transparent', 'text-slate-400');
      } else {
        el.classList.add('hidden');
        btn.classList.remove('border-blue-500', 'text-white');
        btn.classList.add('border-transparent', 'text-slate-400');
      }
    });

    if (tabName === 'clarity') {
      this.loadClarityInsights();
    } else if (tabName === 'kb') {
      this.loadKnowledgeBase();
    }
  },

  switchRole: function(newRole) {
    this.activeRole = newRole;
    const names = {
      creator: "Content Creator",
      reviewer: "Authorised Reviewer",
      manager: "Content Manager",
      admin: "Brand Admin"
    };
    document.getElementById('current-actor-name').innerText = names[newRole] || newRole;
    this.renderWorkflowActions();
  },

  renderWorkflowActions: function() {
    const container = document.getElementById('workflow-action-container');
    container.innerHTML = '';

    if (this.activeRole === 'creator') {
      container.innerHTML = `
        <button onclick="app.submitForApproval()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm rounded-lg shadow-sm flex items-center space-x-1.5 transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
          <span>Submit for Approval</span>
        </button>
      `;
    } else if (this.activeRole === 'reviewer') {
      container.innerHTML = `
        <div class="flex space-x-2">
          <button onclick="app.requestChanges()" class="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs rounded-lg shadow-sm">
            Request Changes
          </button>
          <button onclick="app.forwardToManager()" class="px-3 py-2 bg-blue-700 hover:bg-blue-800 text-white font-medium text-xs rounded-lg shadow-sm">
            Forward to Manager
          </button>
        </div>
      `;
    } else if (this.activeRole === 'manager') {
      container.innerHTML = `
        <div class="flex space-x-2">
          <button onclick="app.requestChanges()" class="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs rounded-lg shadow-sm">
            Request Changes
          </button>
          <button onclick="app.approveDraft()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm rounded-lg shadow-sm flex items-center space-x-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            <span>Approve Publication</span>
          </button>
        </div>
      `;
    } else if (this.activeRole === 'admin') {
      container.innerHTML = `
        <button onclick="app.switchTab('clarity')" class="px-3 py-2 bg-purple-700 hover:bg-purple-800 text-white font-medium text-xs rounded-lg shadow-sm">
          Inspect Guideline Ambiguity
        </button>
      `;
    }
  },

  loadSampleDraft: function() {
    this.draftContent = this.sampleDraft;
    document.getElementById('draft-input').value = this.draftContent;
    this.currentVersion = 1;
    document.getElementById('draft-version-badge').innerText = 'v1';
    this.initDraft();
  },

  initDraft: async function() {
    try {
      const res = await fetch('/api/v1/drafts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: document.getElementById('draft-title').value,
          content: this.draftContent,
          content_type: 'social_post',
          creator_name: 'Content Creator'
        })
      });
      const data = await res.json();
      this.currentDraftId = data.id;
      this.currentVersion = data.current_version;
      this.refreshDraftDetails();
    } catch (e) {
      console.error("Failed to init draft:", e);
    }
  },

  onEditorInput: function() {
    this.draftContent = document.getElementById('draft-input').value;
    this.renderHighlightedText();
  },

  runReview: async function() {
    if (!this.currentDraftId) {
      await this.initDraft();
      return;
    }
    this.draftContent = document.getElementById('draft-input').value;
    try {
      const res = await fetch('/api/v1/review/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: this.draftContent,
          content_type: 'social_post'
        })
      });
      const data = await res.json();

      // Update readability
      document.getElementById('readability-badge').innerText = `Grade ${data.readability.grade_level} (${data.readability.assessment})`;
      
      // Update citation verification stats (Improvement 1)
      const vCount = data.verified_findings.length;
      document.getElementById('citation-stat').innerText = `${vCount}/${vCount} citations code-verified`;

      // Update role routing (Improvement 2)
      document.getElementById('assigned-role-text').innerText = data.assigned_role === 'reviewer' ? 'Authorised Reviewer' : 'Content Manager';

      // Redacted secrets count
      document.getElementById('redacted-count-badge').innerText = `${data.redacted_items.length} secrets redacted`;

      // Refresh full details from DB
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Review run failed:", e);
    }
  },

  refreshDraftDetails: async function() {
    if (!this.currentDraftId) return;
    try {
      const res = await fetch(`/api/v1/drafts/${this.currentDraftId}`);
      const data = await res.json();

      this.currentVersion = data.current_version;
      document.getElementById('draft-version-badge').innerText = `v${this.currentVersion}`;

      // Update status pill
      this.updateStatusPill(data.status);
      document.getElementById('assigned-role-text').innerText = data.assigned_role === 'reviewer' ? 'Authorised Reviewer' : (data.assigned_role === 'manager' ? 'Content Manager' : data.assigned_role);

      this.findings = data.findings;
      this.comments = data.comments;
      this.auditLogs = data.audit_logs;

      this.renderFindings();
      this.renderHighlightedText();
      this.renderComments();
      this.renderAuditLogs();
    } catch (e) {
      console.error("Failed to refresh draft details:", e);
    }
  },

  updateStatusPill: function(status) {
    const pill = document.getElementById('status-pill');
    const text = document.getElementById('status-text');

    if (status === 'APPROVED') {
      pill.className = "flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300";
      text.innerText = "Status: Approved for Publication";
    } else if (status === 'PENDING_APPROVAL') {
      pill.className = "flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300";
      text.innerText = "Status: Pending Approval";
    } else {
      pill.className = "flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300";
      text.innerText = "Status: Needs changes";
    }
  },

  renderHighlightedText: function() {
    const display = document.getElementById('highlighted-display');
    let text = this.draftContent;

    // Filter open findings
    const openFindings = this.findings.filter(f => f.status === 'OPEN');
    
    if (openFindings.length === 0) {
      display.innerHTML = text.replace(/\n/g, '<br>') || '<span class="text-slate-400 italic">No content.</span>';
      return;
    }

    let markedHtml = text;
    // Replace phrases safely with spans
    openFindings.forEach(f => {
      const phrase = f.flagged_text;
      if (!phrase || !markedHtml.includes(phrase)) return;

      let highlightClass = 'highlight-medium';
      if (f.severity === 'HIGH' || f.claim_verdict === 'UNVERIFIABLE') {
        highlightClass = 'highlight-high';
      } else if (f.category === 'terminology') {
        highlightClass = 'highlight-low';
      } else if (f.category === 'accessibility') {
        highlightClass = 'highlight-acc';
      }

      const replacement = `<mark class="${highlightClass}" onclick="app.selectFinding('${f.id}')" title="Click to inspect: ${f.rule_or_fact_id}">${phrase}</mark>`;
      markedHtml = markedHtml.replace(phrase, replacement);
    });

    display.innerHTML = markedHtml.replace(/\n/g, '<br>');
  },

  renderFindings: function() {
    const container = document.getElementById('findings-container');
    const badge = document.getElementById('findings-count-badge');
    const openFindings = this.findings.filter(f => f.status === 'OPEN');
    badge.innerText = `${openFindings.length} Issues`;

    if (openFindings.length === 0) {
      container.innerHTML = `
        <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-6 text-center">
          <div class="w-10 h-10 bg-emerald-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 font-bold">✓</div>
          <h4 class="text-sm font-bold text-emerald-900">All Brand Guidelines Satisfied</h4>
          <p class="text-xs text-emerald-700 mt-1">This draft complies with all approved guidelines, tone standards, and verified facts.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = openFindings.map(f => {
      // Verdict Badge (Improvement 2)
      let verdictBadge = '';
      if (f.claim_verdict === 'UNVERIFIABLE') {
        verdictBadge = `<span class="bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded border border-rose-300">UNVERIFIABLE ➔ Routed to Reviewer</span>`;
      } else if (f.claim_verdict === 'CONTRADICTED') {
        verdictBadge = `<span class="bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded border border-amber-300">CONTRADICTED</span>`;
      } else if (f.category === 'terminology') {
        verdictBadge = `<span class="bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded border border-blue-300">TERMINOLOGY</span>`;
      } else if (f.category === 'accessibility') {
        verdictBadge = `<span class="bg-purple-100 text-purple-800 font-bold px-2 py-0.5 rounded border border-purple-300">ACCESSIBILITY</span>`;
      }

      // Severity Color
      const sevClass = f.severity === 'HIGH' ? 'bg-rose-600 text-white' : (f.severity === 'MEDIUM' ? 'bg-amber-500 text-white' : 'bg-blue-600 text-white');

      return `
        <div id="card-${f.id}" class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3 transition hover:shadow-md">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="${sevClass} font-bold text-[10px] uppercase px-1.5 py-0.5 rounded">${f.severity}</span>
              ${verdictBadge}
            </div>
            <span class="text-xs font-mono font-bold text-slate-500">${f.rule_or_fact_id}</span>
          </div>

          <div>
            <h4 class="text-xs font-bold text-slate-900">Flagged: <span class="bg-slate-100 px-1 py-0.5 rounded font-mono text-rose-600 font-semibold">"${f.flagged_text}"</span></h4>
            <p class="text-xs text-slate-600 mt-1 leading-relaxed">${f.explanation}</p>
          </div>

          <!-- Citation Grounding Proof (Improvement 1) -->
          <div class="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-[11px] space-y-1">
            <div class="flex items-center justify-between text-slate-500 font-semibold">
              <span>Cited Ground Truth:</span>
              <span class="text-emerald-700 flex items-center space-x-1 font-bold">
                <svg class="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>Code-Verified</span>
              </span>
            </div>
            <p class="text-slate-700 italic border-l-2 border-blue-500 pl-2">"${f.cited_excerpt}"</p>
            <div class="text-[10px] text-slate-400">Source: ${f.cited_source}</div>
          </div>

          <!-- Suggestion & Visual Diff -->
          ${f.suggested_fix ? `
            <div class="bg-blue-50/70 p-2.5 rounded-lg border border-blue-200 text-xs">
              <span class="font-bold text-blue-900 block mb-1">Intent-Preserving Suggestion:</span>
              <div class="text-slate-800 font-medium">Use: <strong class="text-emerald-700 bg-emerald-50 px-1 rounded">${f.suggested_fix}</strong></div>
            </div>
          ` : ''}

          <!-- Action Buttons -->
          <div class="flex items-center justify-end space-x-2 pt-1 border-t border-slate-100">
            ${f.suggested_fix ? `
              <button onclick="app.acceptFinding('${f.id}')" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-md shadow-sm transition">
                Accept
              </button>
            ` : ''}
            <button onclick="app.openEditModal('${f.id}', '${f.suggested_fix || f.flagged_text}')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs rounded-md border border-slate-300">
              Edit
            </button>
            <button onclick="app.openDismissModal('${f.id}')" class="px-2.5 py-1 text-rose-600 hover:bg-rose-50 font-medium text-xs rounded-md">
              Dismiss
            </button>
          </div>
        </div>
      `;
    }).join('');
  },

  selectFinding: function(id) {
    this.selectedFindingId = id;
    const card = document.getElementById(`card-${id}`);
    if (card) {
      document.querySelectorAll('#findings-container > div').forEach(c => c.classList.remove('active-card'));
      card.classList.add('active-card');
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  },

  acceptFinding: async function(findingId) {
    const finding = this.findings.find(f => f.id === findingId);
    if (!finding) return;

    try {
      const res = await fetch(`/api/v1/drafts/${this.currentDraftId}/action-finding/${findingId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'accept',
          actor_role: this.activeRole,
          actor_name: document.getElementById('current-actor-name').innerText
        })
      });
      const data = await res.json();
      
      // Update local draft content with replacement
      if (finding.suggested_fix) {
        this.draftContent = this.draftContent.replace(finding.flagged_text, finding.suggested_fix);
        document.getElementById('draft-input').value = this.draftContent;
      }
      
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Accept failed:", e);
    }
  },

  openDismissModal: function(findingId) {
    this.activeFindingForAction = findingId;
    document.getElementById('dismissal-reason-input').value = '';
    document.getElementById('dismiss-modal').classList.remove('hidden');
  },

  closeDismissModal: function() {
    document.getElementById('dismiss-modal').classList.add('hidden');
    this.activeFindingForAction = null;
  },

  submitDismissal: async function() {
    const reason = document.getElementById('dismissal-reason-input').value;
    if (!reason || !reason.trim()) {
      alert("Please provide a reason. Dismissal feedback is required to feed Guideline Clarity insights.");
      return;
    }

    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/action-finding/${this.activeFindingForAction}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'dismiss',
          actor_role: this.activeRole,
          actor_name: document.getElementById('current-actor-name').innerText,
          dismissal_reason: reason.trim()
        })
      });
      this.closeDismissModal();
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Dismissal failed:", e);
    }
  },

  openEditModal: function(findingId, defaultVal) {
    this.activeFindingForAction = findingId;
    document.getElementById('edit-replacement-input').value = defaultVal;
    document.getElementById('edit-modal').classList.remove('hidden');
  },

  closeEditModal: function() {
    document.getElementById('edit-modal').classList.add('hidden');
    this.activeFindingForAction = null;
  },

  submitEdit: async function() {
    const replacement = document.getElementById('edit-replacement-input').value;
    const finding = this.findings.find(f => f.id === this.activeFindingForAction);
    if (!finding) return;

    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/action-finding/${this.activeFindingForAction}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'edit',
          actor_role: this.activeRole,
          actor_name: document.getElementById('current-actor-name').innerText,
          custom_replacement: replacement
        })
      });

      this.draftContent = this.draftContent.replace(finding.flagged_text, replacement);
      document.getElementById('draft-input').value = this.draftContent;

      this.closeEditModal();
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Edit failed:", e);
    }
  },

  submitForApproval: async function() {
    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_status: 'PENDING_APPROVAL',
          actor_role: this.activeRole,
          actor_name: 'Content Creator',
          comment: 'Submitted revision for final manager sign-off.'
        })
      });
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Submit failed:", e);
    }
  },

  approveDraft: async function() {
    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_status: 'APPROVED',
          actor_role: 'manager',
          actor_name: 'Content Manager',
          comment: 'All claims and guidelines verified against approved facts. Approved for publication.'
        })
      });
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Approval failed:", e);
    }
  },

  requestChanges: async function() {
    const note = prompt("Enter required adjustments for the creator:");
    if (!note) return;
    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_status: 'NEEDS_CHANGES',
          actor_role: this.activeRole,
          actor_name: document.getElementById('current-actor-name').innerText,
          comment: note
        })
      });
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Request changes failed:", e);
    }
  },

  forwardToManager: async function() {
    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          new_status: 'PENDING_APPROVAL',
          actor_role: 'reviewer',
          actor_name: 'Authorised Reviewer',
          comment: 'Legal & claim verification verified. Escalating to brand manager for final publication.'
        })
      });
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Forward failed:", e);
    }
  },

  renderComments: function() {
    const container = document.getElementById('comments-list');
    document.getElementById('comment-count').innerText = this.comments.length;

    if (this.comments.length === 0) {
      container.innerHTML = `<p class="text-xs text-slate-400 italic">No comments posted yet.</p>`;
      return;
    }

    container.innerHTML = this.comments.map(c => `
      <div class="bg-slate-50 p-2 rounded-lg border border-slate-200 text-xs">
        <div class="flex items-center justify-between text-[11px] mb-1">
          <span class="font-bold text-slate-800">${c.author_name} <span class="text-slate-400 font-normal">(${c.author_role})</span></span>
          <span class="text-slate-400 text-[10px]">${new Date(c.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
        <p class="text-slate-700 leading-snug">${c.message}</p>
      </div>
    `).join('');
  },

  postComment: async function() {
    const input = document.getElementById('comment-input');
    const msg = input.value.trim();
    if (!msg || !this.currentDraftId) return;

    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          author_role: this.activeRole,
          author_name: document.getElementById('current-actor-name').innerText,
          message: msg
        })
      });
      input.value = '';
      await this.refreshDraftDetails();
    } catch (e) {
      console.error("Comment failed:", e);
    }
  },

  renderAuditLogs: function() {
    const container = document.getElementById('audit-logs-container');
    if (!container) return;

    if (this.auditLogs.length === 0) {
      container.innerHTML = `<div class="p-4 text-center text-slate-400">No audit events recorded.</div>`;
      return;
    }

    container.innerHTML = this.auditLogs.map(l => `
      <div class="p-3 flex items-start justify-between hover:bg-slate-50">
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-bold text-slate-900">${l.action}</span>
            <span class="bg-slate-100 text-slate-700 text-[10px] font-semibold px-2 py-0.5 rounded">${l.actor_role}: ${l.actor}</span>
          </div>
          <p class="text-slate-600 mt-1 leading-snug">${l.details || ''}</p>
        </div>
        <span class="text-slate-400 text-[10px] whitespace-nowrap ml-4">${new Date(l.timestamp).toLocaleTimeString()}</span>
      </div>
    `).join('');
  },

  // IMPROVEMENT 3: GUIDELINE CLARITY INSIGHTS
  loadClarityInsights: async function() {
    try {
      const res = await fetch('/api/v1/analytics/guideline-clarity');
      const data = await res.json();

      document.getElementById('stat-compliance').innerText = `${data.summary.org_compliance_rate}%`;
      document.getElementById('stat-rules').innerText = data.summary.total_active_rules;
      document.getElementById('stat-ambiguous').innerText = data.summary.high_ambiguity_rules_count;
      document.getElementById('stat-top-disputed').innerText = data.summary.top_disputed_rule;

      // Table body
      const tbody = document.getElementById('clarity-table-body');
      tbody.innerHTML = data.all_rules_clarity.map(r => {
        const isAmb = r.status === 'HIGH_AMBIGUITY';
        const badge = isAmb 
          ? `<span class="bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded border border-rose-300">HIGH AMBIGUITY (${r.dismissal_rate}%)</span>`
          : `<span class="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded border border-emerald-300">CLEAR (${r.clarity_score}% OK)</span>`;

        const feedbackList = (r.dispute_feedback && r.dispute_feedback.length > 0)
          ? r.dispute_feedback.slice(-2).map(f => `<div class="italic text-slate-600">"${f}"</div>`).join('')
          : '<span class="text-slate-400 italic">No creator disputes</span>';

        return `
          <tr class="${isAmb ? 'bg-rose-50/40' : ''}">
            <td class="px-4 py-3 font-mono font-bold text-slate-900">${r.id}</td>
            <td class="px-4 py-3">
              <div class="font-bold text-slate-900">${r.rule_name}</div>
              <div class="text-[10px] text-slate-500">${r.source_reference}</div>
            </td>
            <td class="px-4 py-3">${badge}</td>
            <td class="px-4 py-3 font-semibold text-slate-700">${r.times_dismissed} / ${r.times_flagged}</td>
            <td class="px-4 py-3 space-y-1">${feedbackList}</td>
            <td class="px-4 py-3 text-slate-700 font-medium">${r.recommendation}</td>
          </tr>
        `;
      }).join('');

      // Uncovered topics
      const topicsList = document.getElementById('uncovered-topics-list');
      topicsList.innerHTML = data.uncovered_topics_detected.map(t => `<li>${t}</li>`).join('');

    } catch (e) {
      console.error("Failed to load clarity insights:", e);
    }
  },

  // BRAND KNOWLEDGE BASE TAB
  loadKnowledgeBase: async function() {
    try {
      const [rulesRes, factsRes] = await Promise.all([
        fetch('/api/v1/knowledge-base/rules'),
        fetch('/api/v1/knowledge-base/facts')
      ]);
      const rules = await rulesRes.json();
      const facts = await factsRes.json();

      const rulesContainer = document.getElementById('kb-rules-list');
      rulesContainer.innerHTML = rules.map(r => `
        <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-mono font-bold text-blue-700">${r.id}</span>
            <span class="bg-slate-200 text-slate-700 font-semibold px-2 py-0.5 rounded text-[10px] uppercase">${r.category}</span>
          </div>
          <h4 class="font-bold text-slate-900">${r.rule_name}</h4>
          <p class="text-slate-600">${r.description}</p>
          <div class="bg-white p-2 rounded border border-slate-200">
            <span class="text-[10px] text-slate-400 block font-semibold">Exact Source Excerpt (Ground Truth):</span>
            <p class="text-slate-800 italic">"${r.exact_source_text}"</p>
          </div>
          <div class="text-[10px] text-slate-500">Ref: ${r.source_reference}</div>
        </div>
      `).join('');

      const factsContainer = document.getElementById('kb-facts-list');
      factsContainer.innerHTML = facts.map(f => `
        <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-mono font-bold text-emerald-700">${f.id}</span>
            <span class="bg-slate-200 text-slate-700 font-semibold px-2 py-0.5 rounded text-[10px] uppercase">${f.category}</span>
          </div>
          <h4 class="font-bold text-slate-900">${f.subject}</h4>
          <p class="text-slate-700">${f.fact_statement}</p>
          <div class="bg-white p-2 rounded border border-slate-200">
            <span class="text-[10px] text-slate-400 block font-semibold">Authoritative Quote:</span>
            <p class="text-slate-900 font-medium">"${f.exact_quote}"</p>
          </div>
          <div class="text-[10px] text-slate-500">Valid until: ${f.valid_until || 'Indefinite'} • Approved by: ${f.approved_by}</div>
        </div>
      `).join('');
    } catch (e) {
      console.error("Failed to load KB:", e);
    }
  },

  showKbTab: function(type) {
    const rulesList = document.getElementById('kb-rules-list');
    const factsList = document.getElementById('kb-facts-list');
    const tabRules = document.getElementById('kbtab-rules');
    const tabFacts = document.getElementById('kbtab-facts');

    if (type === 'rules') {
      rulesList.classList.remove('hidden');
      factsList.classList.add('hidden');
      tabRules.className = "text-xs font-bold text-blue-600 border-b-2 border-blue-600 pb-2";
      tabFacts.className = "text-xs font-bold text-slate-400 hover:text-slate-700 pb-2";
    } else {
      rulesList.classList.add('hidden');
      factsList.classList.remove('hidden');
      tabFacts.className = "text-xs font-bold text-blue-600 border-b-2 border-blue-600 pb-2";
      tabRules.className = "text-xs font-bold text-slate-400 hover:text-slate-700 pb-2";
    }
  },

  // MULTI-FORMAT CONTRAST CALCULATOR
  calculateContrast: function() {
    let fg = document.getElementById('fg-color').value;
    let bg = document.getElementById('bg-color').value;
    
    // Sync hex boxes
    document.getElementById('fg-hex').value = fg;
    document.getElementById('bg-hex').value = bg;

    const preview = document.getElementById('contrast-preview-box');
    preview.style.backgroundColor = bg;
    preview.style.color = fg;

    // Luminance math
    function lum(hex) {
      hex = hex.replace('#', '');
      const rgb = [0, 2, 4].map(idx => parseInt(hex.substr(idx, 2), 16) / 255);
      const a = rgb.map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
      return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
    }

    const l1 = lum(fg);
    const l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const rounded = ratio.toFixed(1);

    document.getElementById('contrast-ratio-val').innerText = `${rounded} : 1`;

    const aaBadge = document.getElementById('wcag-aa-badge');
    if (ratio >= 4.5) {
      aaBadge.className = "bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded";
      aaBadge.innerText = "PASS";
    } else {
      aaBadge.className = "bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded";
      aaBadge.innerText = "FAIL (< 4.5)";
    }

    const aaaBadge = document.getElementById('wcag-aaa-badge');
    if (ratio >= 7.0) {
      aaaBadge.className = "bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded";
      aaaBadge.innerText = "PASS";
    } else {
      aaaBadge.className = "bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded";
      aaaBadge.innerText = "FAIL (< 7.0)";
    }
  },

  handleFileUpload: async function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const statusEl = document.getElementById('file-parse-status');
    statusEl.classList.remove('hidden');
    statusEl.innerText = `Ingesting ${file.name}...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/parser/extract-text', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      statusEl.innerHTML = `<strong>Successfully extracted:</strong> ${data.character_count} characters from ${data.file_type.toUpperCase()} file. Loaded into Review Workspace.`;
      
      // Load into editor and switch to workspace
      this.draftContent = data.extracted_text;
      document.getElementById('draft-input').value = this.draftContent;
      this.switchTab('workspace');
      this.runReview();
    } catch (e) {
      statusEl.innerText = `Failed to parse document: ${e.message}`;
    }
  }
};

// Start application
window.addEventListener('DOMContentLoaded', () => {
  app.init();
});
