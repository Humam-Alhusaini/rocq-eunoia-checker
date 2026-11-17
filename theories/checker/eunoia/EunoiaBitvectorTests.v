(* Fixed semantic certificates using SMTCoq's verified bit-vector checker.
   No solver, native producer, or generated CPC evaluator is involved. *)
From Stdlib Require Import List Bool Uint63 NArith.
From SMTCoq.utils Require Import PArray CompDec.
From SMTCoq.structures Require Import CompDecInstances.
From SMTCoq.checker.fol Require Import State Terms.
From SMTCoq.checker Require Import MainChecker.
From SMTCoq.checker.eunoia Require Import EunoiaLocal.
Import ListNotations EunoiaLocal.
Local Open Scope uint63_scope.
Local Open Scope array_scope.
Module EunoiaBitvectorTests.
Definition sorts:=make 0 unit_typ_compdec.
Definition funcs:array(Atom.tval sorts):=make 0 (@Atom.Tval sorts ([],Typ.Tbool) true).
Definition atoms:array Atom.atom:=
  (make 3 (Atom.Acop Atom.CO_xH))
    .[1<-Atom.Acop (Atom.CO_BV [true] 1%N)]
    .[2<-Atom.Auop (Atom.UO_BVnot 1%N) 1].
Definition forms:array Form.form:=
  (make 4 Form.Ftrue).[1<-Form.Ffalse]
    .[2<-Form.FbbT 1 [0]].[3<-Form.FbbT 2 [1]].
Definition resolve p a b c:=Command (Checker_Ext.Res p ((make 2 a).[1<-b])) c.
Definition const_program:=[Command (Checker_Ext.BBConst 1 4) [4];resolve 2 0 1 []].
Definition const_witness:=Witness 3 [(0,[5])] const_program 2.
Definition not_program:=[Command (Checker_Ext.BBConst 1 4) [4];
  Command (Checker_Ext.BBNot 2 1 6) [6];resolve 3 0 2 []].
Definition not_witness:=Witness 4 [(0,[7])] not_program 3.
Definition check cs c w:=Atom.wt sorts funcs atoms && @gate sorts funcs atoms forms cs c w.
Example typed_tables:Form.check_form forms && Atom.check_atom atoms && Atom.wt sorts funcs atoms=true.
Proof. vm_compute; reflexivity. Qed.
Example constant_valid:check [] [4] const_witness=true.
Proof. vm_compute; reflexivity. Qed.
Example negation_valid:check [] [6] not_witness=true.
Proof. vm_compute; reflexivity. Qed.
Example missing_dependency:check [] [6]
  (Witness 4 [(0,[7])] [Command(Checker_Ext.BBNot 2 1 6)[6];resolve 3 0 2 []] 3)=false.
Proof. vm_compute; reflexivity. Qed.
Example dependency_out_of_bounds:check [] [6]
  (Witness 4 [(0,[7])] [Command(Checker_Ext.BBNot 2 9 6)[6];resolve 3 0 2 []] 3)=false.
Proof. vm_compute; reflexivity. Qed.
Example destination_not_fresh:check [] [4]
  (Witness 3 [(0,[5])] [Command(Checker_Ext.BBConst 0 4)[4];resolve 2 0 0 []] 2)=false.
Proof. vm_compute; reflexivity. Qed.
Example wrong_result:check [] [4]
  (Witness 3 [(0,[5])] [Command(Checker_Ext.BBConst 1 6)[4];resolve 2 0 1 []] 2)=false.
Proof. vm_compute; reflexivity. Qed.
Example fallback_true_rejected:check [] [4]
  (Witness 4 [(0,[5])] (Command(Checker_Ext.BBConst 3 0)[0]::const_program) 2)=false.
Proof. vm_compute; reflexivity. Qed.
Example invalid_after_conflict:check [] [4]
  (Witness 4 [(0,[5])] (const_program++[Command(Checker_Ext.BBConst 3 99)[]]) 2)=false.
Proof. vm_compute; reflexivity. Qed.
End EunoiaBitvectorTests.
