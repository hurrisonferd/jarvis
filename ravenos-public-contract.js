(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.RavenOSPublicContract = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const HOST_URL = 'https://hurrisonferd.github.io/jarvis/';
  const TOP_KEYS = ['schema','target','host_url','state','god_control','fae','rooms','privacy','proof','packet_id'];
  const GOD_KEYS = ['base_object_count','effective_object_count','registered_ghost_ports','proven_native_owners','staged_native_candidates','active_hold_count','resolved_hold_count'];
  const FAE_KEYS = ['member','stamp','color_emoji','glyph','accent'];
  const ROOM_KEYS = ['room','state','atmosphere','ghost_count','hold_count','absence_count','material_fae'];
  const PRIVACY_KEYS = ['whitelist_only','source_paths_included','transaction_ids_included','source_event_ids_included','haunt_ids_included','flight_ids_included','hashes_included','receipt_bodies_included','owner_event_bodies_included','ledger_entries_included','flight_history_rows_included','secrets_or_tokens_included'];
  const PROOF_KEYS = ['sanitized_projection_source_bound','public_write_executed','public_host_render_proven','automatic_host_invocation_proven','effect_authority'];
  const HOUSE_STATES = new Set(['SETTLED','HOLD','QUIET','ACTIVE','RESIDUAL']);
  const ROOM_STATES = new Set(['ACTIVE','HOLD','RESIDUAL','QUIET']);
  const ATMOSPHERES = new Set(['ACTIVE_HAUNT','LOCKED_HAUNT','RESIDUAL_ECHO','QUIET']);

  function object(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  function exactKeys(value, expected) {
    if (!object(value)) return false;
    const got = Object.keys(value).sort();
    const want = [...expected].sort();
    return got.length === want.length && got.every((key, index) => key === want[index]);
  }

  function nonNegativeInteger(value) {
    return Number.isInteger(value) && value >= 0;
  }

  function safeToken(value) {
    return typeof value === 'string' && /^[A-Z0-9_]{1,64}$/.test(value);
  }

  function stringValue(value) {
    return typeof value === 'string';
  }

  function canonical(value) {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
    return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
  }

  async function sha256Hex(text) {
    const cryptoApi = typeof globalThis !== 'undefined' ? globalThis.crypto : null;
    if (!cryptoApi || !cryptoApi.subtle || typeof TextEncoder === 'undefined') throw new Error('CRYPTO_UNAVAILABLE');
    const digest = await cryptoApi.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(digest)).map(byte => byte.toString(16).padStart(2, '0')).join('').toUpperCase();
  }

  function fail(reason) {
    return {ok:false, reason};
  }

  async function validatePacket(packet) {
    try {
      if (!exactKeys(packet, TOP_KEYS)) return fail('TOP_LEVEL_KEYS');
      if (packet.schema !== 'ravenos.public-handheld.projection.v1') return fail('SCHEMA');
      if (packet.target !== 'JARVIS_HANDHELD') return fail('TARGET');
      if (packet.host_url !== HOST_URL) return fail('HOST_URL');
      if (!HOUSE_STATES.has(packet.state)) return fail('HOUSE_STATE');

      if (!exactKeys(packet.god_control, GOD_KEYS)) return fail('GOD_CONTROL_KEYS');
      if (!GOD_KEYS.every(key => nonNegativeInteger(packet.god_control[key]))) return fail('GOD_CONTROL_VALUES');

      if (!Array.isArray(packet.fae)) return fail('FAE_LIST');
      for (const row of packet.fae) {
        if (!exactKeys(row, FAE_KEYS)) return fail('FAE_KEYS');
        if (!safeToken(row.member)) return fail('FAE_MEMBER');
        if (![row.stamp,row.color_emoji,row.glyph,row.accent].every(stringValue)) return fail('FAE_VALUES');
      }

      if (!Array.isArray(packet.rooms)) return fail('ROOM_LIST');
      for (const row of packet.rooms) {
        if (!exactKeys(row, ROOM_KEYS)) return fail('ROOM_KEYS');
        if (!safeToken(row.room)) return fail('ROOM_NAME');
        if (!ROOM_STATES.has(row.state)) return fail('ROOM_STATE');
        if (!ATMOSPHERES.has(row.atmosphere)) return fail('ROOM_ATMOSPHERE');
        if (![row.ghost_count,row.hold_count,row.absence_count].every(nonNegativeInteger)) return fail('ROOM_COUNTS');
        if (!Array.isArray(row.material_fae) || !row.material_fae.every(safeToken)) return fail('ROOM_FAE');
      }

      if (!exactKeys(packet.privacy, PRIVACY_KEYS)) return fail('PRIVACY_KEYS');
      if (packet.privacy.whitelist_only !== true) return fail('PRIVACY_WHITELIST');
      for (const key of PRIVACY_KEYS) {
        if (key !== 'whitelist_only' && packet.privacy[key] !== false) return fail('PRIVACY_FLAG_' + key.toUpperCase());
      }

      if (!exactKeys(packet.proof, PROOF_KEYS)) return fail('PROOF_KEYS');
      if (packet.proof.sanitized_projection_source_bound !== true) return fail('PROOF_SOURCE_BOUND');
      for (const key of ['public_write_executed','public_host_render_proven','automatic_host_invocation_proven','effect_authority']) {
        if (packet.proof[key] !== false) return fail('PROOF_FLAG_' + key.toUpperCase());
      }

      if (!/^PUBLICHAUNT-[A-F0-9]{24}$/.test(packet.packet_id)) return fail('PACKET_ID_FORMAT');
      const identity = {...packet};
      delete identity.packet_id;
      const digest = await sha256Hex(canonical(identity));
      const expected = 'PUBLICHAUNT-' + digest.slice(0, 24);
      if (packet.packet_id !== expected) return fail('PACKET_ID_MISMATCH');
      return {ok:true, reason:'VALID'};
    } catch (error) {
      return fail(error && error.message ? error.message : 'VALIDATION_ERROR');
    }
  }

  return {
    version: 'ravenos.public-handheld.contract-validator.v1',
    hostUrl: HOST_URL,
    validatePacket,
    canonical,
  };
});
