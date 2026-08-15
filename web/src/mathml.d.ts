import type { HTMLAttributes } from "react";

type MathMLProps = HTMLAttributes<HTMLElement> & {
  display?: "block" | "inline";
  width?: string;
};

declare global {
  namespace JSX {
    interface IntrinsicElements {
      math: MathMLProps;
      mfrac: MathMLProps;
      mi: MathMLProps;
      mn: MathMLProps;
      mo: MathMLProps;
      mrow: MathMLProps;
      mspace: MathMLProps;
      msqrt: MathMLProps;
      msup: MathMLProps;
    }
  }
}

export {};
