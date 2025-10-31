#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ValueTracking.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"
#include <llvm/Transforms/Utils/Mem2Reg.h>

using namespace llvm;

namespace {

struct LICMPass : public PassInfoMixin<LICMPass> {
    void printIR(Module &M) {
        std::error_code err;
        raw_fd_ostream outFile("licm_IR.txt", err, sys::fs::OF_Text);
        if (err) {
            errs() << "Error opening file: " << err.message() << "\n";
            return;
        }

        for (auto &F : M.functions()) {
            F.print(outFile);
        }
    }

    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M) {
            if (F.isDeclaration()) {
                continue;
            }

            auto &FM = AM.getResult<FunctionAnalysisManagerModuleProxy>(M).getManager();
            auto &LI = FM.getResult<LoopAnalysis>(F);

            for (Loop *L : LI) {
                BasicBlock *preheader = L->getLoopPreheader();
                if (!preheader) {
                    continue;
                }

                bool changed = true;

                while (changed) {
                    std::vector<Instruction *> loopInvariants;
                    changed = false;
                    for (auto *B : L->blocks()) {
                        for (auto &I : *B) {
                            if (I.isTerminator() || I.mayHaveSideEffects() || !isSafeToSpeculativelyExecute(&I) ||
                                I.mayReadOrWriteMemory()) {
                                continue;
                            }

                            if (L->hasLoopInvariantOperands(&I)) {
                                errs() << "Loop invariant instruction: " << I << "\n";
                                loopInvariants.push_back(&I);
                                changed = true;
                            }
                        }
                    }
                    for (auto *I : loopInvariants) {
                        I->moveBefore(preheader->getTerminator());
                        errs() << "Moved instruction to preheader: " << *I << "\n";
                    }
                }
            }
        }
        printIR(M);
        return PreservedAnalyses::all();
    }
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "LICM pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(createModuleToFunctionPassAdaptor(PromotePass()));
                    MPM.addPass(LICMPass());
                });
        }
    };
}
