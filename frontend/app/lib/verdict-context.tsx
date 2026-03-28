'use client';

import React, { createContext, useContext, useState } from 'react';
import type { VerdictOutput, ListingInput, DriverProfile } from './shared';
import { DEFAULT_LISTING, DEFAULT_DRIVER } from './shared';

interface VerdictState {
  verdict: VerdictOutput | null;
  setVerdict: (v: VerdictOutput | null) => void;
  formState: ListingInput;
  setFormState: React.Dispatch<React.SetStateAction<ListingInput>>;
  driverState: DriverProfile;
  setDriverState: React.Dispatch<React.SetStateAction<DriverProfile>>;
}

const VerdictContext = createContext<VerdictState | null>(null);

export function VerdictProvider({ children }: { children: React.ReactNode }) {
  const [verdict, setVerdict] = useState<VerdictOutput | null>(null);
  const [formState, setFormState] = useState<ListingInput>(DEFAULT_LISTING);
  const [driverState, setDriverState] = useState<DriverProfile>(DEFAULT_DRIVER);

  return (
    <VerdictContext.Provider value={{ verdict, setVerdict, formState, setFormState, driverState, setDriverState }}>
      {children}
    </VerdictContext.Provider>
  );
}

export function useVerdict() {
  const ctx = useContext(VerdictContext);
  if (!ctx) throw new Error('useVerdict must be used within VerdictProvider');
  return ctx;
}
