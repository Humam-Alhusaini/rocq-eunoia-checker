From Stdlib Require Import List String Bool Arith.
From SMTCoq.checker.eunoia Require Import EoSyntax EoRuntime CpcGenerated.
From SMTCoq.checker.eunoia Require Import LiaTraceReplay CpcDirectRules.
Import ListNotations.
Local Open Scope string_scope.
Definition q:=lia_query [("x",Symbol "Int")].
Definition b op a c:=Apply(Apply(Symbol op)a)c.
Definition input:=b "=" (b "+" (Symbol "x")(Symbol "0"))(Symbol "x").
Definition reference n:=map(fun t=>derive 500 q "arith_poly_norm"[t][])(repeat input n).
Definition direct n:=map(fun t=>CpcDirectRules.derive_context default_primitive 500 q "arith_poly_norm" None[t][])(repeat input n).
Definition expected n xs:=Nat.eqb(List.length xs)n && forallb(fun t=>match t with Some t=>term_eqb t input|_=>false end)xs.
Goal expected 1000(reference 1000)=true.
Proof. Time vm_compute. reflexivity. Time Qed.
Goal expected 1000(direct 1000)=true.
Proof. Time vm_compute. reflexivity. Time Qed.
Goal expected 3000(reference 3000)=true.
Proof. Time vm_compute. reflexivity. Time Qed.
Goal expected 3000(direct 3000)=true.
Proof. Time vm_compute. reflexivity. Time Qed.
