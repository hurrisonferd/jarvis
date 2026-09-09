'use strict';
const fs = require('node:fs');
const path = require('node:path');
const contract = require('../ravenos-public-contract.js');

const ROOT = path.resolve(__dirname, '..');
const PACKET = path.join(ROOT, 'ravenos-public-haunt.json');
const clone = value => JSON.parse(JSON.stringify(value));

async function expectReject(packet, reason) {
  const result = await contract.validatePacket(packet);
  if (result.ok || result.reason !== reason) {
    throw new Error(`expected rejection ${reason}, got ${JSON.stringify(result)}`);
  }
}

async function main() {
  const packet = JSON.parse(fs.readFileSync(PACKET, 'utf8'));
  const current = await contract.validatePacket(packet);
  if (!current.ok) throw new Error(`current packet rejected: ${current.reason}`);

  const legacyGod = clone(packet);
  legacyGod.god_control.fair yos_power_mode = 'MAX_POWER';
  await expectReject(legacyGod, 'GOD_CONTROL_KEYS');

  const privacyLeak = clone(packet);
  privacyLeak.privacy.secrets_or_tokens_included = true;
  await expectReject(privacyLeak, 'PRIVACY_FLAG_SECRETS_OR_TOKENS_INCLUDED');

  const badId = clone(packet);
  badId.packet_id = 'PUBLICHAUNT-000000000000000000000000';
  await expectReject(badId, 'PACKET_ID_MISMATCH');

  const badState = clone(packet);
  badState.state = 'SOURCE_BOUND';
  await expectReject(badState, 'HOUSE_STATE');

  const hostInflation = clone(packet);
  hostInflation.proof.automatic_host_invocation_proven = true;
  await expectReject(hostInflation, 'PROOF_FLAG_AUTOMATIC_HOST_INVOCATION_PROVEN');

  console.log('RAVENOS_PUBLIC_CONTRACT_CANARY PASS');
  console.log(`validator=${contract.version} packet=${packet.packet_id} strict_nested_whitelist=true packet_identity_verified=true`);
}

main().catch(error => {
  console.error(error.stack || error);
  process.exit(1);
});
