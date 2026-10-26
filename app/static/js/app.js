// Verity Frontend Engine — Round 3 Premium Upgrade
// All existing logic preserved. Added: toast notifications, loading states, dark-theme card rendering.

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

  // ─── TOAST NOTIFICATION SYSTEM ───────────────────────────────────────
  showToast: function(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
      success: '<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
      error:   '<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
      warn:    '<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
      info:    '<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} pointer-events-auto`;
    toast.innerHTML = `${icons[type] || icons.info}<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'fadeOut 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  // ─── INIT ─────────────────────────────────────────────────────────────
  init: function() {
    this.draftContent = this.sampleDraft;
    document.getElementById('draft-input').value = this.draftContent;
    this.initDraft();
    this.renderWorkflowActions();
    this.calculateContrast();
  },

  // ─── TAB SWITCHING ────────────────────────────────────────────────────
  switchTab: function(tabName) {
    this.activeTab = tabName;
    ['workspace', 'clarity', 'kb', 'multiformat', 'audit'].forEach(t => {
      const el  = document.getElementById(`view-${t}`);
      const btn = document.getElementById(`tab-${t}`);
      if (t === tabName) {
        el.classList.remove('hidden');
        btn.classList.add('active');
      } else {
        el.classList.add('hidden');
        btn.classList.remove('active');
      }
    });

    if (tabName === 'clarity')  this.loadClarityInsights();
    else if (tabName === 'kb')  this.loadKnowledgeBase();
  },

  // ─── ROLE SWITCHING ───────────────────────────────────────────────────
  switchRole: function(newRole) {
    this.activeRole = newRole;
    const names = {
      creator:  "Content Creator",
      reviewer: "Authorised Reviewer",
      manager:  "Content Manager",
      admin:    "Brand Admin"
    };
    document.getElementById('current-actor-name').innerText = names[newRole] || newRole;
    this.renderWorkflowActions();
    this.showToast(`Role switched to ${names[newRole]}`, 'info');
  },

  // ─── WORKFLOW ACTIONS ─────────────────────────────────────────────────
  renderWorkflowActions: function() {
    const container = document.getElementById('workflow-action-container');
    container.innerHTML = '';

    if (this.activeRole === 'creator') {
      container.innerHTML = `
        <button onclick="app.submitForApproval()" class="btn-success text-xs font-heading px-4 py-2 flex items-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
          Submit for Approval
        </button>
      `;
    } else if (this.activeRole === 'reviewer') {
      container.innerHTML = `
        <div class="flex gap-2">
          <button onclick="app.requestChanges()" class="btn-amber text-xs font-heading px-3 py-2">Request Changes</button>
          <button onclick="app.forwardToManager()" class="btn-primary text-xs font-heading px-3 py-2">Forward to Manager</button>
        </div>
      `;
    } else if (this.activeRole === 'manager') {
      container.innerHTML = `
        <div class="flex gap-2">
          <button onclick="app.requestChanges()" class="btn-amber text-xs font-heading px-3 py-2">Request Changes</button>
          <button onclick="app.approveDraft()" class="btn-success text-xs font-heading px-4 py-2 flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            Approve Publication
          </button>
        </div>
      `;
    } else if (this.activeRole === 'admin') {
      container.innerHTML = `
        <button onclick="app.switchTab('clarity')" class="btn-primary text-xs font-heading px-3 py-2">Inspect Guideline Ambiguity</button>
      `;
    }
  },

  // ─── LOAD SAMPLE DRAFT ────────────────────────────────────────────────
  loadSampleDraft: function() {
    this.draftContent = this.sampleDraft;
    document.getElementById('draft-input').value = this.draftContent;
    this.currentVersion = 1;
    document.getElementById('draft-version-badge').innerText = 'v1';
    this.initDraft();
    this.showToast('Hackathon test draft loaded!', 'info');
  },

  // ─── INIT DRAFT ───────────────────────────────────────────────────────
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

  // ─── EDITOR INPUT ─────────────────────────────────────────────────────
  onEditorInput: function() {
    this.draftContent = document.getElementById('draft-input').value;
    this.renderHighlightedText();
  },

  // ─── RUN REVIEW ───────────────────────────────────────────────────────
  runReview: async function() {
    if (!this.currentDraftId) {
      await this.initDraft();
      return;
    }

    // Loading state
    const btn   = document.getElementById('run-btn');
    const icon  = document.getElementById('run-icon');
    const label = document.getElementById('run-label');
    btn.disabled = true;
    btn.style.opacity = '0.7';
    icon.classList.add('spin');
    label.textContent = 'Scanning…';

    // Show skeleton loading
    this.showSkeletonFindings();

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
      this.showToast(`Audit complete — ${vCount} verified finding${vCount !== 1 ? 's' : ''} found.`, vCount > 0 ? 'warn' : 'success');
    } catch (e) {
      console.error("Review run failed:", e);
      this.showToast('Review failed — check backend connection.', 'error');
    } finally {
      btn.disabled = false;
      btn.style.opacity = '1';
      icon.classList.remove('spin');
      label.textContent = 'Re-run & Audit';
    }
  },

  // ─── SKELETON LOADING ─────────────────────────────────────────────────
  showSkeletonFindings: function() {
    const container = document.getElementById('findings-container');
    container.innerHTML = [1,2,3].map(() => `
      <div class="card-surface2 rounded-xl p-4 space-y-3">
        <div class="shimmer h-4 w-2/3 rounded"></div>
        <div class="shimmer h-3 w-full rounded"></div>
        <div class="shimmer h-3 w-5/6 rounded"></div>
        <div class="shimmer h-16 rounded-lg"></div>
        <div class="flex justify-end gap-2">
          <div class="shimmer h-7 w-16 rounded-lg"></div>
          <div class="shimmer h-7 w-16 rounded-lg"></div>
        </div>
      </div>
    `).join('');
  },

  // ─── REFRESH DRAFT DETAILS ────────────────────────────────────────────
  refreshDraftDetails: async function() {
    if (!this.currentDraftId) return;
    try {
      const res = await fetch(`/api/v1/drafts/${this.currentDraftId}`);
      const data = await res.json();

      this.currentVersion = data.current_version;
      document.getElementById('draft-version-badge').innerText = `v${this.currentVersion}`;

      this.updateStatusPill(data.status);
      document.getElementById('assigned-role-text').innerText =
        data.assigned_role === 'reviewer' ? 'Authorised Reviewer' :
        (data.assigned_role === 'manager' ? 'Content Manager' : data.assigned_role);

      this.findings  = data.findings;
      this.comments  = data.comments;
      this.auditLogs = data.audit_logs;

      this.renderFindings();
      this.renderHighlightedText();
      this.renderComments();
      this.renderAuditLogs();
    } catch (e) {
      console.error("Failed to refresh draft details:", e);
    }
  },

  // ─── STATUS PILL ──────────────────────────────────────────────────────
  updateStatusPill: function(status) {
    const pill = document.getElementById('status-pill');
    const text = document.getElementById('status-text');

    if (status === 'APPROVED') {
      pill.style.cssText = "background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);color:#6EE7B7;display:flex;align-items:center;gap:6px;padding:4px 12px;border-radius:9999px;font-size:0.75rem;font-weight:700;font-family:'Space Grotesk',sans-serif;";
      text.innerText = "Status: Approved for Publication";
    } else if (status === 'PENDING_APPROVAL') {
      pill.style.cssText = "background:rgba(103,232,249,0.1);border:1px solid rgba(103,232,249,0.3);color:#67E8F9;display:flex;align-items:center;gap:6px;padding:4px 12px;border-radius:9999px;font-size:0.75rem;font-weight:700;font-family:'Space Grotesk',sans-serif;";
      text.innerText = "Status: Pending Approval";
    } else {
      pill.style.cssText = "background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);color:#FCD34D;display:flex;align-items:center;gap:6px;padding:4px 12px;border-radius:9999px;font-size:0.75rem;font-weight:700;font-family:'Space Grotesk',sans-serif;";
      text.innerText = "Status: Needs Changes";
    }
  },

  // ─── HIGHLIGHTED TEXT ─────────────────────────────────────────────────
  renderHighlightedText: function() {
    const display = document.getElementById('highlighted-display');
    let text = this.draftContent;

    const openFindings = this.findings.filter(f => f.status === 'OPEN');

    if (openFindings.length === 0) {
      display.innerHTML = text.replace(/\n/g, '<br>') || '<span style="color:var(--text-secondary);font-style:italic;">No content.</span>';
      return;
    }

    let markedHtml = text;
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

  // ─── RENDER FINDINGS ──────────────────────────────────────────────────
  renderFindings: function() {
    const container = document.getElementById('findings-container');
    const badge     = document.getElementById('findings-count-badge');
    const openFindings = this.findings.filter(f => f.status === 'OPEN');
    badge.innerText = `${openFindings.length} Issue${openFindings.length !== 1 ? 's' : ''}`;

    if (openFindings.length === 0) {
      container.innerHTML = `
        <div class="card-surface2 rounded-xl p-8 text-center">
          <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 font-bold text-xl"
               style="background:rgba(16,185,129,0.15);color:#10B981;">✓</div>
          <h4 class="font-heading text-sm font-bold" style="color:#6EE7B7;">All Brand Guidelines Satisfied</h4>
          <p class="text-xs mt-1" style="color:var(--text-secondary);">This draft complies with all approved guidelines, tone standards, and verified facts.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = openFindings.map(f => {
      // Verdict Badge
      let verdictBadge = '';
      if (f.claim_verdict === 'UNVERIFIABLE') {
        verdictBadge = `<span class="badge badge-red font-heading">UNVERIFIABLE → Routed to Reviewer</span>`;
      } else if (f.claim_verdict === 'CONTRADICTED') {
        verdictBadge = `<span class="badge badge-amber font-heading">CONTRADICTED</span>`;
      } else if (f.category === 'terminology') {
        verdictBadge = `<span class="badge badge-cyan font-heading">TERMINOLOGY</span>`;
      } else if (f.category === 'accessibility') {
        verdictBadge = `<span class="badge badge-violet font-heading">ACCESSIBILITY</span>`;
      }

      // Severity glow border colour
      const sevBg   = f.severity === 'HIGH'   ? 'rgba(244,63,94,0.12)'  :
                      f.severity === 'MEDIUM' ? 'rgba(245,158,11,0.1)'  : 'rgba(103,232,249,0.08)';
      const sevBdr  = f.severity === 'HIGH'   ? 'rgba(244,63,94,0.35)'  :
                      f.severity === 'MEDIUM' ? 'rgba(245,158,11,0.3)'  : 'rgba(103,232,249,0.25)';
      const sevAccent = f.severity === 'HIGH'   ? '#F43F5E'  :
                        f.severity === 'MEDIUM' ? '#F59E0B'  : '#67E8F9';
      const sevLabel  = f.severity === 'HIGH'   ? 'HIGH'  :
                        f.severity === 'MEDIUM' ? 'MED'   : 'LOW';

      return `
        <div id="card-${f.id}"
             class="rounded-xl p-4 space-y-3 transition-all"
             style="background:${sevBg};border:1px solid ${sevBdr};border-left:3px solid ${sevAccent};">

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="badge font-heading"
                    style="background:${sevBg};border-color:${sevBdr};color:${sevAccent};">${sevLabel}</span>
              ${verdictBadge}
            </div>
            <span class="mono text-[10px] font-bold" style="color:var(--text-secondary);">${f.rule_or_fact_id}</span>
          </div>

          <div>
            <h4 class="font-heading text-xs font-bold" style="color:var(--text-primary);">
              Flagged: <span class="mono rounded px-1.5 py-0.5" style="color:${sevAccent};background:rgba(255,255,255,0.05);">"${f.flagged_text}"</span>
            </h4>
            <p class="text-xs mt-1 leading-relaxed" style="color:var(--text-secondary);">${f.explanation}</p>
          </div>

          <!-- Citation Ground Truth -->
          <div class="rounded-lg p-2.5 text-[11px] space-y-1" style="background:rgba(8,11,24,0.6);border:1px solid var(--border-subtle);">
            <div class="flex items-center justify-between font-semibold" style="color:var(--text-secondary);">
              <span class="font-heading">Cited Ground Truth:</span>
              <span class="flex items-center gap-1" style="color:#10B981;font-weight:700;">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                Code-Verified
              </span>
            </div>
            <p class="italic leading-relaxed" style="color:var(--text-primary);border-left:2px solid var(--violet-primary);padding-left:8px;">"${f.cited_excerpt}"</p>
            <div class="text-[10px]" style="color:var(--ink-muted,#6B7094);">Source: ${f.cited_source}</div>
          </div>

          <!-- Suggestion -->
          ${f.suggested_fix ? `
            <div class="rounded-lg p-2.5 text-xs" style="background:rgba(103,232,249,0.06);border:1px solid rgba(103,232,249,0.2);">
              <span class="font-heading font-bold block mb-1" style="color:var(--cyan-accent);">Intent-Preserving Suggestion:</span>
              <div style="color:var(--text-primary);">Use: <strong class="mono rounded px-1" style="color:#10B981;background:rgba(16,185,129,0.1);">${f.suggested_fix}</strong></div>
            </div>
          ` : ''}

          <!-- Actions -->
          <div class="flex items-center justify-end gap-2 pt-1" style="border-top:1px solid var(--border-subtle);">
            ${f.suggested_fix ? `
              <button onclick="app.acceptFinding('${f.id}')"
                      class="btn-success text-[11px] font-heading px-3 py-1">Accept</button>
            ` : ''}
            <button onclick="app.openEditModal('${f.id}', '${(f.suggested_fix || f.flagged_text).replace(/'/g,"\\'")}' )"
                    class="btn-secondary text-[11px] font-heading px-2.5 py-1">Edit</button>
            <button onclick="app.openDismissModal('${f.id}')"
                    class="btn-danger text-[11px] font-heading px-2.5 py-1">Dismiss</button>
          </div>
        </div>
      `;
    }).join('');
  },

  // ─── SELECT FINDING ───────────────────────────────────────────────────
  selectFinding: function(id) {
    this.selectedFindingId = id;
    document.querySelectorAll('#findings-container > div').forEach(c => c.classList.remove('active-card'));
    const card = document.getElementById(`card-${id}`);
    if (card) {
      card.classList.add('active-card');
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  },

  // ─── ACCEPT FINDING ───────────────────────────────────────────────────
  acceptFinding: async function(findingId) {
    const finding = this.findings.find(f => f.id === findingId);
    if (!finding) return;

    try {
      await fetch(`/api/v1/drafts/${this.currentDraftId}/action-finding/${findingId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'accept',
          actor_role: this.activeRole,
          actor_name: document.getElementById('current-actor-name').innerText
        })
      });

      if (finding.suggested_fix) {
        this.draftContent = this.draftContent.replace(finding.flagged_text, finding.suggested_fix);
        document.getElementById('draft-input').value = this.draftContent;
      }

      await this.refreshDraftDetails();
      this.showToast('Suggestion accepted and applied!', 'success');
    } catch (e) {
      console.error("Accept failed:", e);
      this.showToast('Accept failed — try again.', 'error');
    }
  },

  // ─── DISMISS MODAL ────────────────────────────────────────────────────
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
      this.showToast('Please provide a reason — dismissal feedback is required to feed Guideline Clarity insights.', 'warn');
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
      this.showToast('Finding dismissed — reason logged to Guideline Insights.', 'info');
    } catch (e) {
      console.error("Dismissal failed:", e);
      this.showToast('Dismissal failed — try again.', 'error');
    }
  },

  // ─── EDIT MODAL ───────────────────────────────────────────────────────
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
      this.showToast('Custom replacement applied!', 'success');
    } catch (e) {
      console.error("Edit failed:", e);
      this.showToast('Edit failed — try again.', 'error');
    }
  },

  // ─── WORKFLOW TRANSITIONS ─────────────────────────────────────────────
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
      this.showToast('Draft submitted for approval!', 'success');
    } catch (e) {
      console.error("Submit failed:", e);
      this.showToast('Submission failed — try again.', 'error');
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
      this.showToast('Draft approved for publication! 🎉', 'success');
    } catch (e) {
      console.error("Approval failed:", e);
      this.showToast('Approval failed — try again.', 'error');
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
      this.showToast('Changes requested — creator notified.', 'warn');
    } catch (e) {
      console.error("Request changes failed:", e);
      this.showToast('Request failed — try again.', 'error');
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
      this.showToast('Escalated to Content Manager!', 'info');
    } catch (e) {
      console.error("Forward failed:", e);
      this.showToast('Escalation failed — try again.', 'error');
    }
  },

  // ─── COMMENTS ─────────────────────────────────────────────────────────
  renderComments: function() {
    const container = document.getElementById('comments-list');
    document.getElementById('comment-count').innerText = this.comments.length;

    if (this.comments.length === 0) {
      container.innerHTML = `<p class="text-xs italic" style="color:var(--text-secondary);">No comments posted yet.</p>`;
      return;
    }

    container.innerHTML = this.comments.map(c => `
      <div class="rounded-lg p-2.5 text-xs" style="background:var(--bg-elevated);border:1px solid var(--border-subtle);">
        <div class="flex items-center justify-between text-[11px] mb-1">
          <span class="font-heading font-bold" style="color:var(--text-primary);">${c.author_name}
            <span class="font-normal" style="color:var(--text-secondary);">(${c.author_role})</span>
          </span>
          <span style="color:var(--text-secondary);">${new Date(c.created_at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</span>
        </div>
        <p class="leading-snug" style="color:var(--text-primary);">${c.message}</p>
      </div>
    `).join('');
  },

  postComment: async function() {
    const input = document.getElementById('comment-input');
    const msg   = input.value.trim();
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
      this.showToast('Comment posted!', 'success');
    } catch (e) {
      console.error("Comment failed:", e);
      this.showToast('Comment failed — try again.', 'error');
    }
  },

  // ─── AUDIT LOGS ───────────────────────────────────────────────────────
  renderAuditLogs: function() {
    const container = document.getElementById('audit-logs-container');
    if (!container) return;

    if (this.auditLogs.length === 0) {
      container.innerHTML = `<div class="p-6 text-center text-xs italic" style="color:var(--text-secondary);">No audit events recorded.</div>`;
      return;
    }

    container.innerHTML = this.auditLogs.map(l => `
      <div class="p-3 flex items-start justify-between text-xs hover:bg-white/2 transition-colors"
           style="border-bottom:1px solid var(--border-subtle);">
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-heading font-bold" style="color:var(--text-primary);">${l.action}</span>
            <span class="badge badge-slate font-heading">${l.actor_role}: ${l.actor}</span>
          </div>
          <p class="leading-snug" style="color:var(--text-secondary);">${l.details || ''}</p>
        </div>
        <span class="mono text-[10px] whitespace-nowrap ml-4 mt-0.5" style="color:var(--text-secondary);">
          ${new Date(l.timestamp).toLocaleTimeString()}
        </span>
      </div>
    `).join('');
  },

  // ─── GUIDELINE CLARITY INSIGHTS (Improvement 3) ───────────────────────
  loadClarityInsights: async function() {
    try {
      const res  = await fetch('/api/v1/analytics/guideline-clarity');
      const data = await res.json();

      document.getElementById('stat-compliance').innerText = `${data.summary.org_compliance_rate}%`;
      document.getElementById('stat-rules').innerText      = data.summary.total_active_rules;
      document.getElementById('stat-ambiguous').innerText  = data.summary.high_ambiguity_rules_count;
      document.getElementById('stat-top-disputed').innerText = data.summary.top_disputed_rule;

      // Table body
      const tbody = document.getElementById('clarity-table-body');
      tbody.innerHTML = data.all_rules_clarity.map(r => {
        const isAmb = r.status === 'HIGH_AMBIGUITY';
        const badge = isAmb
          ? `<span class="badge badge-red font-heading">HIGH AMBIGUITY (${r.dismissal_rate}%)</span>`
          : `<span class="badge badge-green font-heading">CLEAR (${r.clarity_score}% OK)</span>`;

        const feedbackList = (r.dispute_feedback && r.dispute_feedback.length > 0)
          ? r.dispute_feedback.slice(-2).map(f => `<div class="italic" style="color:var(--text-secondary);">"${f}"</div>`).join('')
          : `<span class="italic" style="color:var(--text-secondary);">No creator disputes</span>`;

        return `
          <tr style="background:${isAmb ? 'rgba(244,63,94,0.05)' : 'transparent'};border-bottom:1px solid var(--border-subtle);">
            <td class="px-4 py-3 mono font-bold" style="color:var(--violet-light);">${r.id}</td>
            <td class="px-4 py-3">
              <div class="font-heading font-bold" style="color:var(--text-primary);">${r.rule_name}</div>
              <div class="text-[10px] mt-0.5" style="color:var(--text-secondary);">${r.source_reference}</div>
            </td>
            <td class="px-4 py-3">${badge}</td>
            <td class="px-4 py-3 font-heading font-semibold" style="color:var(--text-primary);">${r.times_dismissed} / ${r.times_flagged}</td>
            <td class="px-4 py-3 space-y-1 text-xs">${feedbackList}</td>
            <td class="px-4 py-3 text-xs" style="color:var(--text-secondary);">${r.recommendation}</td>
          </tr>
        `;
      }).join('');

      // Uncovered topics
      const topicsList = document.getElementById('uncovered-topics-list');
      topicsList.innerHTML = data.uncovered_topics_detected.map(t =>
        `<li class="flex items-center gap-2">
          <span style="color:var(--amber-status);">●</span>
          <span>${t}</span>
        </li>`
      ).join('');

    } catch (e) {
      console.error("Failed to load clarity insights:", e);
      this.showToast('Could not load Guideline Insights — check API.', 'error');
    }
  },

  // ─── KNOWLEDGE BASE ───────────────────────────────────────────────────
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
        <div class="card-surface2 rounded-xl p-4 space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="mono font-bold" style="color:var(--violet-light);">${r.id}</span>
            <span class="badge badge-slate font-heading uppercase">${r.category}</span>
          </div>
          <h4 class="font-heading font-bold" style="color:var(--text-primary);">${r.rule_name}</h4>
          <p style="color:var(--text-secondary);">${r.description}</p>
          <div class="rounded-lg p-2.5" style="background:rgba(8,11,24,0.6);border:1px solid var(--border-subtle);">
            <span class="text-[10px] font-heading font-bold block mb-1" style="color:var(--text-secondary);">Exact Source Excerpt (Ground Truth):</span>
            <p class="italic" style="color:var(--text-primary);">"${r.exact_source_text}"</p>
          </div>
          <div class="text-[10px]" style="color:var(--text-secondary);">Ref: ${r.source_reference}</div>
        </div>
      `).join('');

      const factsContainer = document.getElementById('kb-facts-list');
      factsContainer.innerHTML = facts.map(f => `
        <div class="card-surface2 rounded-xl p-4 space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="mono font-bold" style="color:#10B981;">${f.id}</span>
            <span class="badge badge-green font-heading uppercase">${f.category}</span>
          </div>
          <h4 class="font-heading font-bold" style="color:var(--text-primary);">${f.subject}</h4>
          <p style="color:var(--text-secondary);">${f.fact_statement}</p>
          <div class="rounded-lg p-2.5" style="background:rgba(8,11,24,0.6);border:1px solid var(--border-subtle);">
            <span class="text-[10px] font-heading font-bold block mb-1" style="color:var(--text-secondary);">Authoritative Quote:</span>
            <p class="font-medium" style="color:var(--text-primary);">"${f.exact_quote}"</p>
          </div>
          <div class="text-[10px]" style="color:var(--text-secondary);">Valid until: ${f.valid_until || 'Indefinite'} • Approved by: ${f.approved_by}</div>
        </div>
      `).join('');

    } catch (e) {
      console.error("Failed to load KB:", e);
      this.showToast('Knowledge Base load failed.', 'error');
    }
  },

  showKbTab: function(type) {
    const rulesList = document.getElementById('kb-rules-list');
    const factsList = document.getElementById('kb-facts-list');
    const tabRules  = document.getElementById('kbtab-rules');
    const tabFacts  = document.getElementById('kbtab-facts');

    if (type === 'rules') {
      rulesList.classList.remove('hidden');
      factsList.classList.add('hidden');
      tabRules.style.cssText = "color:var(--violet-light);border-bottom-color:var(--violet-primary);";
      tabFacts.style.cssText = "color:var(--text-secondary);border-bottom-color:transparent;";
    } else {
      rulesList.classList.add('hidden');
      factsList.classList.remove('hidden');
      tabFacts.style.cssText = "color:var(--violet-light);border-bottom-color:var(--violet-primary);";
      tabRules.style.cssText = "color:var(--text-secondary);border-bottom-color:transparent;";
    }
  },

  // ─── WCAG CONTRAST CALCULATOR ─────────────────────────────────────────
  calculateContrast: function() {
    let fg = document.getElementById('fg-color').value;
    let bg = document.getElementById('bg-color').value;

    document.getElementById('fg-hex').value = fg;
    document.getElementById('bg-hex').value = bg;

    const preview = document.getElementById('contrast-preview-box');
    preview.style.backgroundColor = bg;
    preview.style.color = fg;

    function lum(hex) {
      hex = hex.replace('#', '');
      const rgb = [0, 2, 4].map(idx => parseInt(hex.substr(idx, 2), 16) / 255);
      const a   = rgb.map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
      return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
    }

    const l1    = lum(fg);
    const l2    = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

    document.getElementById('contrast-ratio-val').innerText = `${ratio.toFixed(1)} : 1`;

    const aaBadge  = document.getElementById('wcag-aa-badge');
    const aaaBadge = document.getElementById('wcag-aaa-badge');

    if (ratio >= 4.5) {
      aaBadge.className = 'badge badge-green font-heading';
      aaBadge.innerText = 'PASS';
    } else {
      aaBadge.className = 'badge badge-red font-heading';
      aaBadge.innerText = 'FAIL (< 4.5)';
    }

    if (ratio >= 7.0) {
      aaaBadge.className = 'badge badge-green font-heading';
      aaaBadge.innerText = 'PASS';
    } else {
      aaaBadge.className = 'badge badge-red font-heading';
      aaaBadge.innerText = 'FAIL (< 7.0)';
    }
  },

  // ─── FILE UPLOAD ──────────────────────────────────────────────────────
  handleFileUpload: async function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const statusEl = document.getElementById('file-parse-status');
    statusEl.classList.remove('hidden');
    statusEl.innerText = `Ingesting ${file.name}…`;
    this.showToast(`Parsing ${file.name}…`, 'info');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res  = await fetch('/api/v1/parser/extract-text', { method: 'POST', body: formData });
      const data = await res.json();
      statusEl.innerHTML = `<strong style="color:var(--cyan-accent);">Successfully extracted:</strong> ${data.character_count} characters from ${data.file_type.toUpperCase()} file. Loaded into Review Workspace.`;

      this.draftContent = data.extracted_text;
      document.getElementById('draft-input').value = this.draftContent;
      this.switchTab('workspace');
      this.runReview();
      this.showToast(`${file.name} parsed — auto-running audit!`, 'success');
    } catch (e) {
      statusEl.innerText = `Failed to parse document: ${e.message}`;
      this.showToast('File parse failed.', 'error');
    }
  }
};

// Start application
window.addEventListener('DOMContentLoaded', () => {
  app.init();
});
