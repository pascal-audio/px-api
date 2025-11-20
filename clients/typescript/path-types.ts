/**
 * Path-to-Type Mappings
 * 
 * Auto-generated from japi_path_registry.json
 * DO NOT EDIT MANUALLY
 */

import type * as Types from "./schemas.typebox";

// Type aliases for registry -> generated type name mappings
export type DeviceSetup = Types.DeviceSetupView;
export type AudioSetup = Types.AudioSetupView;

/** Paths that don't require parameters */
export type StaticPath =
   "/"
 | "/audio/input/config"
 | "/audio/input/generator"
 | "/audio/output/speaker_ways"
 | "/audio/output/summing_matrix"
 | "/gpio"
 | "/install"
 | "/network"
 | "/network/lan1"
 | "/network/lan2"
 | "/power"
;

/** Paths that require channel parameter (1-4) */
export type ChannelPath =
   "/audio/input/analog/${number}"
 | "/audio/input/digital/${number}"
 | "/audio/input/network/${number}"
 | "/audio/output/digital/${number}"
 | "/audio/output/network/${number}"
 | "/audio/output/speaker/${number}"
 | "/audio/output/speaker/${number}/array"
 | "/audio/output/speaker/${number}/array/eq"
 | "/audio/output/speaker/${number}/array/fir"
 | "/audio/output/speaker/${number}/preset"
 | "/audio/output/speaker/${number}/preset/clip_limiter"
 | "/audio/output/speaker/${number}/preset/crossover"
 | "/audio/output/speaker/${number}/preset/eq"
 | "/audio/output/speaker/${number}/preset/fir"
 | "/audio/output/speaker/${number}/preset/peak_limiter"
 | "/audio/output/speaker/${number}/preset/rms_limiter"
 | "/audio/output/speaker/${number}/user"
 | "/audio/output/speaker/${number}/user/eq"
;

/** Paths that require channel and band parameters */
export type BandPath =
   "/audio/output/speaker/${number}/array/eq/bands/${number}"
 | "/audio/output/speaker/${number}/preset/eq/bands/${number}"
 | "/audio/output/speaker/${number}/user/eq/bands/${number}"
;

/** All valid API paths */
export type ValidPath = StaticPath | ChannelPath | BandPath;

/** Maps paths to their GET return types */
export interface PathTypeMap {
  /** Complete device setup configuration */
  "/": Types.DeviceSetupView;
  /** Global input configuration and routing */
  "/audio/input/config": Types.InputConfig;
  /** Test signal generator settings */
  "/audio/input/generator": Types.GeneratorSetup;
  /** Speaker way mapping for multi-way systems */
  "/audio/output/speaker_ways": Types.SpeakerWayMapping;
  /** Input-to-output routing matrix */
  "/audio/output/summing_matrix": number[][];
  /** GPIO pin configuration */
  "/gpio": Types.Gpio;
  /** User-editable device metadata */
  "/install": Types.InstallInfo;
  /** Network mode (split/redundant) configuration */
  "/network": Types.NetworkSetup;
  /** LAN1 network interface configuration */
  "/network/lan1": Types.LanSetup;
  /** LAN2 network interface configuration */
  "/network/lan2": Types.LanSetup;
  /** Power modes and protection settings */
  "/power": Types.PowerManagement;
  /** Analog input channel (XLR/TRS) */
  "/audio/input/analog/${number}": Types.InputChannel;
  /** Digital input channel (AES/SPDIF) */
  "/audio/input/digital/${number}": Types.InputChannel;
  /** Network audio input (Dante) */
  "/audio/input/network/${number}": Types.InputChannel;
  /** Digital output channel (AES/EBU) */
  "/audio/output/digital/${number}": Types.DigitalOutputChannel;
  /** Network audio output (Dante) */
  "/audio/output/network/${number}": Types.DigitalOutputChannel;
  /** Speaker channel settings (name, sources, mute) */
  "/audio/output/speaker/${number}": Types.SpeakerOutputChannel;
  /** Array processing (gain, polarity, delay) */
  "/audio/output/speaker/${number}/array": Types.ArrayProcessing;
  /** Array 5-band parametric EQ */
  "/audio/output/speaker/${number}/array/eq": Types.Equalizer;
  /** Array FIR filter coefficients */
  "/audio/output/speaker/${number}/array/fir": Types.ArrayFirFilter;
  /** Preset processing (drive, gain, polarity, delay) */
  "/audio/output/speaker/${number}/preset": Types.PresetProcessing;
  /** Preset hard clip protection */
  "/audio/output/speaker/${number}/preset/clip_limiter": Types.ClipLimiter;
  /** Preset crossover filters (HPF + LPF) */
  "/audio/output/speaker/${number}/preset/crossover": Types.Crossover;
  /** Preset 15-band parametric EQ */
  "/audio/output/speaker/${number}/preset/eq": Types.Equalizer;
  /** Preset FIR filter coefficients */
  "/audio/output/speaker/${number}/preset/fir": Types.PresetFirFilter;
  /** Preset fast peak limiter */
  "/audio/output/speaker/${number}/preset/peak_limiter": Types.PeakLimiter;
  /** Preset thermal/RMS limiter */
  "/audio/output/speaker/${number}/preset/rms_limiter": Types.RmsLimiter;
  /** User processing (gain, polarity, delay, mute, HPF) */
  "/audio/output/speaker/${number}/user": Types.UserProcessing;
  /** User 10-band parametric EQ */
  "/audio/output/speaker/${number}/user/eq": Types.Equalizer;
  /** Array EQ single band parameters */
  "/audio/output/speaker/${number}/array/eq/bands/${number}": Types.EqualizerBand;
  /** Preset EQ single band parameters */
  "/audio/output/speaker/${number}/preset/eq/bands/${number}": Types.EqualizerBand;
  /** User EQ single band parameters */
  "/audio/output/speaker/${number}/user/eq/bands/${number}": Types.EqualizerBand;
}

/** Maps paths to their SET parameter types (patches) */
export interface PathPatchMap {
  /** Global input configuration and routing */
  "/audio/input/config": Types.InputConfigPatch;
  /** Test signal generator settings */
  "/audio/input/generator": Types.GeneratorSetupPatch;
  /** GPIO pin configuration */
  "/gpio": Types.GpioPatch;
  /** User-editable device metadata */
  "/install": Types.InstallInfoPatch;
  /** Network mode (split/redundant) configuration */
  "/network": Types.NetworkSetupPatch;
  /** LAN1 network interface configuration */
  "/network/lan1": Types.LanSetupPatch;
  /** LAN2 network interface configuration */
  "/network/lan2": Types.LanSetupPatch;
  /** Power modes and protection settings */
  "/power": Types.PowerManagementPatch;
  /** Analog input channel (XLR/TRS) */
  "/audio/input/analog/${number}": Types.InputChannelPatch;
  /** Digital input channel (AES/SPDIF) */
  "/audio/input/digital/${number}": Types.InputChannelPatch;
  /** Network audio input (Dante) */
  "/audio/input/network/${number}": Types.InputChannelPatch;
  /** Digital output channel (AES/EBU) */
  "/audio/output/digital/${number}": Types.DigitalOutputChannelPatch;
  /** Network audio output (Dante) */
  "/audio/output/network/${number}": Types.DigitalOutputChannelPatch;
  /** Speaker channel settings (name, sources, mute) */
  "/audio/output/speaker/${number}": Types.SpeakerOutputChannelPatch;
  /** Array processing (gain, polarity, delay) */
  "/audio/output/speaker/${number}/array": Types.ArrayProcessingPatch;
  /** Array 5-band parametric EQ */
  "/audio/output/speaker/${number}/array/eq": Types.EqualizerPatch;
  /** Array FIR filter coefficients */
  "/audio/output/speaker/${number}/array/fir": Types.ArrayFirFilterPatch;
  /** Preset processing (drive, gain, polarity, delay) */
  "/audio/output/speaker/${number}/preset": Types.PresetProcessingPatch;
  /** Preset hard clip protection */
  "/audio/output/speaker/${number}/preset/clip_limiter": Types.ClipLimiterPatch;
  /** Preset crossover filters (HPF + LPF) */
  "/audio/output/speaker/${number}/preset/crossover": Types.CrossoverPatch;
  /** Preset 15-band parametric EQ */
  "/audio/output/speaker/${number}/preset/eq": Types.EqualizerPatch;
  /** Preset FIR filter coefficients */
  "/audio/output/speaker/${number}/preset/fir": Types.PresetFirFilterPatch;
  /** Preset fast peak limiter */
  "/audio/output/speaker/${number}/preset/peak_limiter": Types.PeakLimiterPatch;
  /** Preset thermal/RMS limiter */
  "/audio/output/speaker/${number}/preset/rms_limiter": Types.RmsLimiterPatch;
  /** User processing (gain, polarity, delay, mute, HPF) */
  "/audio/output/speaker/${number}/user": Types.UserProcessingPatch;
  /** User 10-band parametric EQ */
  "/audio/output/speaker/${number}/user/eq": Types.EqualizerPatch;
  /** Array EQ single band parameters */
  "/audio/output/speaker/${number}/array/eq/bands/${number}": Types.EqualizerBandPatch;
  /** Preset EQ single band parameters */
  "/audio/output/speaker/${number}/preset/eq/bands/${number}": Types.EqualizerBandPatch;
  /** User EQ single band parameters */
  "/audio/output/speaker/${number}/user/eq/bands/${number}": Types.EqualizerBandPatch;
}
