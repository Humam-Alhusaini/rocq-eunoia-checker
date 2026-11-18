(* Solver-free certificates for structural bit-vector operations. *)
From Stdlib Require Import List Bool Uint63 NArith.
From SMTCoq.utils Require Import PArray CompDec.
From SMTCoq.structures Require Import CompDecInstances.
From SMTCoq.checker.fol Require Import State Terms.
From SMTCoq.checker Require Import MainChecker.
From SMTCoq.checker.eunoia Require Import EunoiaLocal.
Import ListNotations EunoiaLocal.
Local Open Scope uint63_scope.
Local Open Scope array_scope.
Module EunoiaBitvectorStructureTests.
Definition sorts:=make 0 unit_typ_compdec.
Definition funcs:array(Atom.tval sorts):=make 0 (@Atom.Tval sorts ([],Typ.Tbool) true).
Definition atoms:array Atom.atom:=
  (make 8 (Atom.Acop Atom.CO_xH))
    .[1<-Atom.Acop(Atom.CO_BV [true;false] 2%N)]
    .[2<-Atom.Acop(Atom.CO_BV [false;true] 2%N)]
    .[3<-Atom.Abop(Atom.BO_BVconcat 2%N 2%N) 1 2]
    .[4<-Atom.Auop(Atom.UO_BVextr 0%N 2%N 4%N) 3]
    .[5<-Atom.Auop(Atom.UO_BVzextn 2%N 2%N) 1]
    .[6<-Atom.Auop(Atom.UO_BVsextn 2%N 2%N) 2]
    .[7<-Atom.Auop(Atom.UO_BVextr 3%N 2%N 4%N) 3].
Definition forms:array Form.form:=
  (make 10 Form.Ftrue).[1<-Form.Ffalse]
    .[2<-Form.FbbT 1 [0;2]].[3<-Form.FbbT 2 [2;0]]
    .[4<-Form.FbbT 3 [2;0;0;2]].[5<-Form.FbbT 4 [2;0]]
    .[6<-Form.FbbT 5 [0;2;2;2]].[7<-Form.FbbT 6 [2;0;0;0]]
    .[8<-Form.FbbT 6 [2;0;2;2]].[9<-Form.FbbT 7 [2;2]].
Definition resolve p a b:=Command(Checker_Ext.Res p ((make 2 a).[1<-b]))[].
Definition constants:=[Command(Checker_Ext.BBConst 1 4)[4];Command(Checker_Ext.BBConst 2 6)[6]].
Definition concat_program:=constants++[Command(Checker_Ext.BBConcat 3 1 2 8)[8]].
Definition check cs c w:=Atom.wt sorts funcs atoms && @gate sorts funcs atoms forms cs c w.
Example typed_tables:Form.check_form forms && Atom.check_atom atoms && Atom.wt sorts funcs atoms=true.
Proof. vm_compute; reflexivity. Qed.
Example concat_valid:check [] [8] (Witness 5 [(0,[9])] (concat_program++[resolve 4 0 3]) 4)=true.
Proof. vm_compute; reflexivity. Qed.
Example extract_valid:check [] [10] (Witness 6 [(0,[11])]
  (concat_program++[Command(Checker_Ext.BBExtract 4 3 10)[10];resolve 5 0 4]) 5)=true.
Proof. vm_compute; reflexivity. Qed.
Example zero_extend_valid:check [] [12] (Witness 4 [(0,[13])]
  [Command(Checker_Ext.BBConst 1 4)[4];Command(Checker_Ext.BBZextend 2 1 12)[12];resolve 3 0 2] 3)=true.
Proof. vm_compute; reflexivity. Qed.
Example sign_extend_valid:check [] [14] (Witness 4 [(0,[15])]
  [Command(Checker_Ext.BBConst 1 6)[6];Command(Checker_Ext.BBSextend 2 1 14)[14];resolve 3 0 2] 3)=true.
Proof. vm_compute; reflexivity. Qed.
Example wrong_concat_order:check [] [8] (Witness 5 [(0,[9])]
  (constants++[Command(Checker_Ext.BBConcat 3 2 1 8)[8];resolve 4 0 3]) 4)=false.
Proof. vm_compute; reflexivity. Qed.
Example wrong_sign_fill:check [] [16] (Witness 4 [(0,[17])]
  [Command(Checker_Ext.BBConst 1 6)[6];Command(Checker_Ext.BBSextend 2 1 16)[16];resolve 3 0 2] 3)=false.
Proof. vm_compute; reflexivity. Qed.
Example missing_input:check [] [10] (Witness 3 [(0,[11])]
  [Command(Checker_Ext.BBExtract 1 2 10)[10];resolve 2 0 1] 2)=false.
Proof. vm_compute; reflexivity. Qed.
Example extraction_outside_source:check [] [18] (Witness 6 [(0,[19])]
  (concat_program++[Command(Checker_Ext.BBExtract 4 3 18)[18];resolve 5 0 4]) 5)=false.
Proof. vm_compute; reflexivity. Qed.
Example invalid_after_conflict:check [] [8] (Witness 6 [(0,[9])]
  (concat_program++[resolve 4 0 3;Command(Checker_Ext.BBExtract 5 3 99)[]]) 4)=false.
Proof. vm_compute; reflexivity. Qed.
End EunoiaBitvectorStructureTests.
