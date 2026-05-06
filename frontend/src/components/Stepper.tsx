import { Check } from 'lucide-react';
import type { ReactNode } from 'react';

interface StepperProps {
  steps: string[];
  activeIndex: number;
}

export function Stepper({ steps, activeIndex }: StepperProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-soft backdrop-blur">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        {steps.map((step, index) => {
          const active = index <= activeIndex;
          const current = index === activeIndex;
          return (
            <div key={step} className="flex flex-1 items-center gap-3">
              <div
                className={`grid h-10 w-10 shrink-0 place-items-center rounded-full border transition-all duration-200 ${
                  active
                    ? 'border-blue-500 bg-gradient-to-br from-blue-500 to-indigo-500 text-white shadow-glow'
                    : 'border-slate-700 bg-slate-950 text-slate-500'
                }`}
              >
                {index < activeIndex ? <Check className="h-4 w-4" /> : <span className="text-sm font-semibold">{index + 1}</span>}
              </div>
              <div className="min-w-0">
                <p className={`text-sm font-medium ${current ? 'text-white' : active ? 'text-slate-200' : 'text-slate-500'}`}>
                  {step}
                </p>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-300 ${
                      active ? 'w-full' : 'w-0'
                    }`}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}